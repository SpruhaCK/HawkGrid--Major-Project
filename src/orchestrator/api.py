from dotenv import load_dotenv
load_dotenv()

import os
import logging
import joblib
import pandas as pd
from typing import Optional
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict

from src.orchestrator.playbook import execute_playbook
from src.orchestrator.detector import detect_event
from src.orchestrator.report_writer import build_report, append_report
from src.blockchain.ledger_factory import get_ledger
from src.cloud.provider_factory import get_cloud_providers

# =========================
# GLOBAL STATE
# =========================

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("hawkgrid-api")

MODEL_PATH = os.getenv("HG_MODEL_PATH", "src/ml/hawkgrid_pipeline.joblib")
IP_MAPPING_CACHE = {}

# =========================
# ASSET DISCOVERY
# =========================

def refresh_asset_cache(app: FastAPI):
    global IP_MAPPING_CACHE
    IP_MAPPING_CACHE = {}

    providers = getattr(app.state, "providers", {})

    for name, provider in providers.items():
        try:
            assets = provider.discover_assets()

            for asset in assets:
                pub = asset.get("public_ip")
                priv = asset.get("private_ip")

                if pub and priv:
                    IP_MAPPING_CACHE[pub] = {
                        "private_ip": priv,
                        "provider": provider
                    }

                    log.info(f"[{name}] {pub} -> {priv}")

        except Exception as e:
            log.error(f"Asset discovery failed for {name}: {e}")


def resolve_asset(public_ip: str):
    if public_ip in IP_MAPPING_CACHE:
        return IP_MAPPING_CACHE[public_ip]

    return {
        "private_ip": public_ip,
        "provider": None
    }

# =========================
# FASTAPI LIFESPAN
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("🔥 LIFESPAN STARTED")
    app.state.providers = get_cloud_providers()
    app.state.ledger = get_ledger()

    try:
        log.info("Loading ML model...")
        data = joblib.load(MODEL_PATH)
        app.state.model = data
        log.info("Model loaded.")
    except Exception as e:
        log.error(f"ML load failed: {e}")

    refresh_asset_cache(app)

    yield

    log.info("Shutting down.")


app = FastAPI(
    title="HawkGrid Detection Core",
    version="2.2",
    lifespan=lifespan
)

# =========================
# DATA MODEL
# =========================

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

# =========================
# DETECTION ROUTE
# =========================

@app.post("/api/detect")
def detect_anomaly(payload: LogFeatures):
    try:
        ledger = app.state.ledger
        resolved = resolve_asset(payload.dst_ip)
        
        incident_data = payload.model_dump()
        incident_data["node_id"] = resolved["private_ip"]
        provider = resolved["provider"]

        df = pd.DataFrame([payload.model_dump()])
        detection = detect_event(df)

        incident_data["anomaly_score"] = detection.get("anomaly_score", 0.0)
        incident_data["attack_type"] = detection.get("attack_type", "NORMAL")
        incident_data["raw_event"] = payload.model_dump()
        
        response_action_status = "SIMULATED_SUCCESS"

        if detection.get("is_anomaly") and detection.get("attack_type") != "NORMAL" and provider:
            response_action = execute_playbook(
                "AUTOMATED_CONTAINMENT",
                incident_data,
                provider
            )
            response_action_status = response_action.get("status", "FAILED")
        else:
            response_action = {"action": "NONE", "status": "NORMAL_TRAFFIC"}
            if not detection.get("is_anomaly"):
                response_action_status = "SIMULATED_SUCCESS" 

        print(f"DEBUG: Attempting to log to ledger for {payload.dst_ip}...") 
        ledger.log_incident(incident_data, response_action_status)
        print("DEBUG: Ledger log_incident call finished.")

        report = build_report(payload.model_dump(), detection, response_action)
        append_report(report)

        return {
            "detection": detection,
            "response": response_action
        }

    except Exception as e:
        log.exception("Detection failure")
        raise HTTPException(status_code=500, detail=str(e))

# =========================
# STATUS ROUTE
# =========================

@app.get("/status")
def status():
    providers = getattr(app.state, "providers", {})

    return {
        "service": "HawkGrid Detection Core",
        "online": True,
        "providers": list(providers.keys()),
        "protected_assets": list(IP_MAPPING_CACHE.keys())
    }

# =========================
# RUN
# =========================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
