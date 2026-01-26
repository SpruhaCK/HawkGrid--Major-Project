"""
api.py

HawkGrid Detection Core
- Real-time anomaly detection
- AWS CloudTrail ingestion
- Automated incident response
"""

import sys
import os
import time
import json
import logging
from typing import Optional
from contextlib import asynccontextmanager

# --- PATH SETUP ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# --- THIRD PARTY ---
import joblib
import boto3
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, ConfigDict

# --- LOCAL IMPORTS ---
from src.ml.preprocess import preprocess_security_logs
from src.orchestrator.playbook import execute_playbook

# --- LEDGER SELECTION ---
USE_LOCAL_LEDGER = os.getenv("USE_LOCAL_LEDGER", "false").lower() == "true"

if USE_LOCAL_LEDGER:
    from src.blockchain.ledger import log_incident_to_ledger
else:
    try:
        from src.blockchain.ledger_aws import log_incident_to_ledger
    except ImportError:
        from src.blockchain.ledger import log_incident_to_ledger
        USE_LOCAL_LEDGER = True

# --- OPTIONAL ELASTIC ---
try:
    from elasticsearch import Elasticsearch
except Exception:
    Elasticsearch = None

# --- CONFIG ---
MODEL_PATH = os.getenv("HG_MODEL_PATH", "src/ml/hawkgrid_pipeline.joblib")
LOG_DIR = os.getenv("HG_LOG_DIR", "logs")
ANOMALY_LOG_PATH = os.path.join(LOG_DIR, "anomalies.jsonl")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ES_HOST = os.getenv("ELASTICSEARCH_HOSTS", "http://elasticsearch-1:9200")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger("hawkgrid-api")

# --- AWS CLIENTS ---
cloudtrail = boto3.client("cloudtrail", region_name=AWS_REGION)

# =========================
# FASTAPI LIFESPAN
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
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
        log.error("Startup failed: %s", e)

    yield
    log.info("HawkGrid Core shutting down.")

app = FastAPI(
    title="HawkGrid Detection Core",
    version="1.0",
    lifespan=lifespan
)

# =========================
# DATA MODELS
# =========================
class LogFeatures(BaseModel):
    model_config = ConfigDict(extra="allow")

    node_id: Optional[str] = Field(default="unknown-node")
    cloud_provider: Optional[str] = Field(default="unknown-cloud")
    timestamp: Optional[str] = Field(
        default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    )

# =========================
# HELPERS
# =========================
def append_anomaly_log(entry: dict):
    with open(ANOMALY_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")

def normalize_aws_event(event: dict) -> dict:
    return {
        "node_id": event.get("Username", "aws-user"),
        "cloud_provider": "aws",
        "API_Call_Freq": 1,
        "Failed_Auth_Count": 1 if event.get("ErrorCode") else 0,
        "Network_Egress_MB": 0.0,
        "timestamp": event.get("EventTime")
    }

# =========================
# ROUTES
# =========================
@app.get("/status")
def status(request: Request):
    state = request.app.state
    ready = all([
        hasattr(state, "scaler"),
        hasattr(state, "model_iso"),
        hasattr(state, "model_rf")
    ])
    return {
        "service": "HawkGrid Detection Core",
        "online": True,
        "models_loaded": ready,
        "feature_count": len(state.features) if ready else 0
    }

@app.post("/api/detect")
def detect_anomaly(payload: LogFeatures, request: Request):
    state = request.app.state

    if not hasattr(state, "model_iso"):
        raise HTTPException(status_code=503, detail="ML models not loaded")

    raw = pd.DataFrame([payload.model_dump()])

    try:
        X = preprocess_security_logs(raw, expected_features=state.features)
        X_scaled = state.scaler.transform(X)

        iso_pred = state.model_iso.predict(X_scaled)[0]
        score = float(state.model_iso.decision_function(X_scaled)[0])
        is_anomaly = iso_pred == -1

        if is_anomaly:
            rf_enc = int(state.model_rf.predict(X_scaled)[0])
            attack = state.label_encoder.inverse_transform([rf_enc])[0]
        else:
            attack = "Normal"

        response = {
            "node_id": payload.node_id,
            "cloud_provider": payload.cloud_provider,
            "timestamp": payload.timestamp,
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": round(score, 6),
            "attack_type_classified": attack
        }

        if is_anomaly and attack != "Normal":
            incident = {
                "timestamp": response["timestamp"],
                "node_id": response["node_id"],
                "cloud_provider": response["cloud_provider"],
                "anomaly_score": response["anomaly_score"],
                "attack_type": attack,
                "raw_event": raw.iloc[0].to_dict()
            }

            append_anomaly_log(incident)

            response["forensic_ledger"] = log_incident_to_ledger(
                incident,
                response_action="AUTOMATED_CONTAINMENT"
            )

            response["incident_response"] = execute_playbook(
                "AUTOMATED_CONTAINMENT",
                incident
            )

        return response

    except Exception as e:
        log.exception("Detection error")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest/aws")
def ingest_aws_events(request: Request):
    events = cloudtrail.lookup_events(MaxResults=10)
    results = []

    for e in events.get("Events", []):
        normalized = normalize_aws_event(e)
        payload = LogFeatures(**normalized)
        res = detect_anomaly(payload, request)
        results.append(res)

    return {
        "source": "aws-cloudtrail",
        "events_processed": len(results),
        "results": results
    }

@app.get("/health/es")
def health_es():
    if Elasticsearch is None:
        raise HTTPException(status_code=501, detail="Elasticsearch not installed")

    es = Elasticsearch([ES_HOST])
    if not es.ping():
        raise HTTPException(status_code=503, detail="Elasticsearch unavailable")

    return {"status": "ok", "cluster": es.info().get("cluster_name")}

# =========================
# LOCAL RUN
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
