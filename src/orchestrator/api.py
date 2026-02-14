import sys
import os
import time
import logging
import joblib
import boto3
import pandas as pd
from typing import Optional, List
from contextlib import asynccontextmanager
from datetime import datetime

# --- PATH SETUP ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, ConfigDict
from fastapi.encoders import jsonable_encoder

# --- LOCAL IMPORTS ---
from src.orchestrator.playbook import execute_playbook
from src.orchestrator.detector import detect_event
from src.orchestrator.report_writer import build_report, append_report
from src.orchestrator.attack_mapper import map_attack_to_features

# --- GLOBAL STATE ---
IP_MAPPING_CACHE = {} 
USE_LOCAL_LEDGER = os.getenv("USE_LOCAL_LEDGER", "false").lower() == "true"  # <-- uncomment this line to use AWS QLDB instead of local ledger
# USE_LOCAL_LEDGER = os.getenv("USE_LOCAL_LEDGER", "true").lower() == "true" # <-- Uncomment this line to use local ledger instead of AWS QLDB

if USE_LOCAL_LEDGER:
    from src.blockchain.ledger import log_incident_to_ledger
else:
    from src.blockchain.ledger_aws import log_incident_to_ledger

# --- CONFIG ---
MODEL_PATH = os.getenv("HG_MODEL_PATH", "src/ml/hawkgrid_pipeline.joblib")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("hawkgrid-api")

# =========================
# ASSET DISCOVERY HELPERS
# =========================

def refresh_asset_cache():
    """Builds the mapping of Public IPs to Private IPs on startup."""
    global IP_MAPPING_CACHE
    try:
        ec2 = boto3.client('ec2', region_name=AWS_REGION)
        # Search for your specific instances by Tag Name
        response = ec2.describe_instances(Filters=[
            {'Name': 'tag:Name', 'Values': ['HawkGrid-Linux-Victim', 'HawkGrid-Windows-Victim']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ])
        
        for res in response['Reservations']:
            for inst in res['Instances']:
                pub = inst.get('PublicIpAddress')
                priv = inst.get('PrivateIpAddress')
                if pub and priv:
                    IP_MAPPING_CACHE[pub] = priv
                    log.info(f"Mapped {pub} (Public) -> {priv} (Private)")
    except Exception as e:
        log.error(f"Failed to refresh asset cache: {e}")

def resolve_asset_id(public_ip: str) -> str:
    """Translates a changing Public IP to a static Private IP for the Asset Database."""
    # Check cache first
    if public_ip in IP_MAPPING_CACHE:
        return IP_MAPPING_CACHE[public_ip]
    
    # Fallback: Individual lookup if cache missed
    try:
        ec2 = boto3.client('ec2', region_name=AWS_REGION)
        response = ec2.describe_instances(Filters=[{'Name': 'ip-address', 'Values': [public_ip]}])
        for res in response['Reservations']:
            for inst in res['Instances']:
                priv = inst.get('PrivateIpAddress')
                IP_MAPPING_CACHE[public_ip] = priv
                return priv
    except Exception:
        pass
    
    return public_ip # Return original if not found

# =========================
# FASTAPI LIFESPAN
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Load ML Models
    try:
        log.info("Loading ML pipeline: %s", MODEL_PATH)
        data = joblib.load(MODEL_PATH)
        app.state.scaler = data["scaler"]
        app.state.label_encoder = data["label_encoder"]
        app.state.model_iso = data["model_iso"]
        app.state.model_rf = data["model_rf"]
        app.state.features = data["features"]
        log.info("ML models loaded successfully.")
    except Exception as e:
        log.error(f"ML Load Failed: {e}")

    # 2. Refresh Cloud Asset Cache
    refresh_asset_cache()
    
    yield
    log.info("HawkGrid Core shutting down.")

app = FastAPI(title="HawkGrid Detection Core", version="1.0", lifespan=lifespan)

# =========================
# DATA MODELS
# =========================
class LogFeatures(BaseModel):
    model_config = ConfigDict(extra="allow")
    node_id: Optional[str] = "unknown-node"
    dst_ip: str
    src_ip: str
    API_Call_Freq: float = 0.0
    Failed_Auth_Count: float = 0.0
    Network_Egress_MB: float = 0.0
    cloud_provider: str = "aws"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

# =========================
# CORE DETECTION LOGIC
# =========================

def run_detection(payload: LogFeatures):
    raw_dict = payload.model_dump()
    
    # STEP 1: RESOLVE ASSET (Public IP -> Static Private IP)
    static_node_id = resolve_asset_id(raw_dict['dst_ip'])
    payload.node_id = static_node_id
    raw_dict['node_id'] = static_node_id # Sync dictionary
    
    # STEP 2: ML DETECTION
    # Ensure the DataFrame has only the features the ML model expects
    raw_df = pd.DataFrame([raw_dict])
    detection = detect_event(raw_df)
    
    response_action = {"action": "NONE", "status": "NO_ACTION"}

    # STEP 3: INCIDENT RESPONSE
    if detection["is_anomaly"]:
        incident = {
            "timestamp": payload.timestamp,
            "node_id": payload.node_id, # Now the static Private IP
            "src_ip": payload.src_ip,
            "dst_ip": payload.dst_ip,
            "cloud_provider": payload.cloud_provider,
            "anomaly_score": detection["anomaly_score"],
            "attack_type": detection["attack_type"],
            "raw_event": raw_dict
        }

        # This triggers the Boto3/Security Group block in playbook.py
        response_action = execute_playbook("AUTOMATED_CONTAINMENT", incident)
        
        # Cryptographic Ledger logging
        try:
            log_incident_to_ledger(incident, response_action["status"])
        except Exception as e:
            log.error(f"Ledger Write Failed: {e}")

    # STEP 4: REPORTING
    report = build_report(raw_dict, detection, response_action)
    append_report(report)
    
    return report

# =========================
# ROUTES
# =========================
@app.post("/api/detect")
def detect_anomaly(payload: LogFeatures):
    try:
        return run_detection(payload)
    except Exception as e:
        log.exception("Detection error")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def status(request: Request):
    state = request.app.state
    ready = all([hasattr(state, "scaler"), hasattr(state, "model_iso")])
    return {
        "service": "HawkGrid Detection Core",
        "online": True,
        "models_ready": ready,
        "protected_assets": list(IP_MAPPING_CACHE.keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)