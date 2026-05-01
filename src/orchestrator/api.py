from dotenv import load_dotenv
load_dotenv()

import os
import time
import logging
import joblib
import pandas as pd
import requests
import csv
from typing import Optional
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict

# Cloud & Response Imports
from src.orchestrator.playbook import execute_playbook
from src.orchestrator.detector import detect_event
from src.orchestrator.report_writer import build_report, append_report
from src.blockchain.ledger_factory import get_ledger
from src.cloud.provider_factory import get_cloud_providers
from src.response.hive_mind import execute_cross_cloud_quarantine, execute_standard_block

# Azure Imports (Uncomment when you have Azure keys)
# from azure.monitor.query import LogsQueryClient
# from azure.identity import DefaultAzureCredential

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("hawkgrid-api")

MODEL_PATH = os.getenv("HG_MODEL_PATH", "src/ml/hawkgrid_pipeline.joblib")
IP_MAPPING_CACHE = {}

def log_mttr_to_csv(attack_type: str, attacker_ip: str, mttr_seconds: float):
    os.makedirs('reports', exist_ok=True)
    file_path = 'reports/mttr_logs.csv'
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Attack_Type', 'Attacker_IP', 'MTTR_Seconds'])
        writer.writerow([attack_type, attacker_ip, round(mttr_seconds, 4)])

def refresh_asset_cache(app: FastAPI):
    global IP_MAPPING_CACHE
    IP_MAPPING_CACHE = {}
    providers = getattr(app.state, "providers", {})
    
    print(f"\n[*] Rebuilding Asset Cache. Active Providers: {list(providers.keys())}")
    
    for name, provider in providers.items():
        try:
            assets = provider.discover_assets()
            print(f"    -> {name.upper()} returned {len(assets)} raw assets: {assets}")
            
            for asset in assets:
                pub = asset.get("public_ip")
                priv = asset.get("private_ip", "unknown-internal")
                
                # We only strictly need the public IP for the dashboard!
                if pub:
                    IP_MAPPING_CACHE[pub] = {"private_ip": priv, "provider": provider}
                    print(f"    ✅ Cached successfully: {pub} ({name.upper()})")
                else:
                    print(f"    ❌ Skipped: Asset missing Public IP -> {asset}")
        except Exception as e:
            log.error(f"Asset discovery failed for {name}: {e}")

def resolve_asset(public_ip: str):
    return IP_MAPPING_CACHE.get(public_ip, {"private_ip": public_ip, "provider": None})

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.providers = get_cloud_providers()
    app.state.ledger = get_ledger()
    try:
        app.state.model = joblib.load(MODEL_PATH)
        log.info("ML pipeline loaded.")
    except Exception as e:
        log.error(f"ML load failed: {e}")

    refresh_asset_cache(app)
    
    # 🚨 HAWKGRID SHIELD: Discover Presenter's IP
    try:
        print("[*] Discovering Current Network Public IP for Whitelisting...")
        host_public_ip = requests.get('https://api.ipify.org', timeout=5).text.strip()
        app.state.whitelisted_ip = host_public_ip
        print(f"[*] 🛡️ HawkGrid Shield Active: Will not block current network ({host_public_ip})")
    except Exception as e:
        print(f"[!] Warning: Could not determine Public IP. Defaulting to localhost.")
        app.state.whitelisted_ip = "127.0.0.1"
        
    yield
    log.info("Shutting down.")

app = FastAPI(title="HawkGrid Detection Core", version="2.5", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class LogFeatures(BaseModel):
    model_config = ConfigDict(extra="allow")
    node_id: Optional[str] = "unknown-node"
    dst_ip: str
    src_ip: str
    API_Call_Freq: float = 0.0
    Failed_Auth_Count: float = 0.0
    Network_Egress_MB: float = 0.0
    cloud_provider: str = "unknown"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@app.post("/api/detect")
def detect_anomaly(payload: LogFeatures):
    try:
        start_time = time.time()
        resolved = resolve_asset(payload.dst_ip)
        incident_data = payload.model_dump()
        incident_data["node_id"] = resolved["private_ip"]
        provider = resolved["provider"]

        df = pd.DataFrame([payload.model_dump()])
        detection = detect_event(df)
        
        incident_data.update({
            "anomaly_score": detection.get("anomaly_score", 0.0),
            "attack_type": detection.get("attack_type", "NORMAL"),
            "severity": detection.get("severity", "LOW"),
            "owasp_risk_score": detection.get("owasp_risk_score", 0),
            "raw_event": payload.model_dump()
        })

        response_action_status = "NORMAL_TRAFFIC"
        response_action = {"action": "NONE", "status": "NO_ACTION"}
        mttr_recorded = False

        if detection.get("is_anomaly") and incident_data["attack_type"] != "NORMAL" and provider:
            risk_score = detection.get("owasp_risk_score", 0)
            
            # 🚨 Pass the Shield IP to both mitigation strategies!
            if risk_score >= 4:
                response_action = execute_cross_cloud_quarantine(
                    incident_data, provider.name, app.state.providers, app.state.whitelisted_ip
                )
            else:
                response_action = execute_standard_block(
                    incident_data, provider.name, app.state.providers, app.state.whitelisted_ip
                )
            
            response_action_status = response_action.get("status", "FAILED")
            mttr_seconds = time.time() - start_time
            mttr_recorded = True

        if mttr_recorded:
            print(f"\n[METRIC] ⚡ MTTR for {incident_data['attack_type']} from {payload.src_ip}: {mttr_seconds:.4f} seconds\n")
            log_mttr_to_csv(incident_data['attack_type'], payload.src_ip, mttr_seconds)

        app.state.ledger.log_incident(incident_data, response_action_status)
        report = build_report(payload.model_dump(), detection, response_action)
        append_report(report)

        return {"detection": detection, "response": response_action}
    except Exception as e:
        log.exception("Detection failure")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def status(request: Request):
    global IP_MAPPING_CACHE
    
    # Auto-Heal: If React asks for IPs but the cache is empty, scan AWS again!
    if not IP_MAPPING_CACHE:
        print("\n[*] Dashboard requested status, but cache is empty! Auto-healing...")
        refresh_asset_cache(request.app)

    asset_list = []
    
    for pub_ip, info in IP_MAPPING_CACHE.items():
        provider_name = info["provider"].name if info["provider"] else "unknown"
        asset_list.append({
            "ip": pub_ip,
            "provider": provider_name.upper(),
            "name": f"HawkGrid-{provider_name.capitalize()}-Node",
            "region": "Auto-Discovered"
        })

    print(f"[*] Sending {len(asset_list)} assets to React Dashboard.")
    
    return {
        "service": "HawkGrid Detection Core",
        "online": True,
        "assets": asset_list
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)