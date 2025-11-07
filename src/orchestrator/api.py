"""
api.py

FastAPI service that loads the hawkgrid pipeline and exposes endpoints:
- GET /status
- POST /api/detect  (accepts arbitrary features as JSON)
- GET /health/es

It writes anomaly events to logs/anomalies.jsonl and calls src.blockchain.ledger.log_incident_to_ledger
when anomalies are detected and need forensic logging.
"""
import os
import time
import json
import joblib
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np

# local imports (your repo)
from src.ml.preprocess import preprocess_security_logs
# ledger function - keep your existing ledger function signature
from src.blockchain.ledger import log_incident_to_ledger

# Optional Elastic import: handle if not installed in dev env
try:
    from elasticsearch import Elasticsearch
except Exception:
    Elasticsearch = None

# CONFIG
MODEL_PATH = os.getenv("HG_MODEL_PATH", "src/ml/hawkgrid_pipeline.joblib")
LOG_DIR = os.getenv("HG_LOG_DIR", "logs")
ANOMALY_LOG_PATH = os.path.join(LOG_DIR, "anomalies.jsonl")
ES_HOST = os.getenv("ELASTICSEARCH_HOSTS", "http://elasticsearch-1:9200")

os.makedirs(LOG_DIR, exist_ok=True)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("hawkgrid-api")

# FastAPI app
app = FastAPI(title="HawkGrid Detection Core", version="1.0")

# Global model handles
scaler = None
label_encoder = None
model_iso = None
model_rf = None
model_features = None

# Pydantic model (flexible)
class LogFeatures(BaseModel):
    # accept arbitrary fields (extra allowed)
    node_id: Optional[str] = Field(default="unknown-node")
    cloud_provider: Optional[str] = Field(default="unknown-cloud")
    timestamp: Optional[str] = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

    class Config:
        extra = "allow"


@app.on_event("startup")
def startup_load_models():
    global scaler, label_encoder, model_iso, model_rf, model_features
    try:
        models = joblib.load(MODEL_PATH)
        scaler = models["scaler"]
        label_encoder = models["label_encoder"]
        model_iso = models["model_iso"]
        model_rf = models["model_rf"]
        model_features = models["features"]
        log.info("Loaded ML pipeline from %s", MODEL_PATH)
    except FileNotFoundError:
        log.error("Model file not found at %s. Run training first.", MODEL_PATH)
    except Exception as e:
        log.exception("Failed to load model pipeline: %s", e)


@app.get("/status")
def status():
    ready = all([scaler, label_encoder, model_iso, model_rf])
    return {
        "service": "HawkGrid Detection Core",
        "online": True,
        "models_loaded": ready,
        "feature_count": len(model_features) if model_features else 0
    }


def append_anomaly_log(entry: dict):
    """Append one JSON line to anomalies.jsonl (safe append)."""
    try:
        with open(ANOMALY_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        log.exception("Failed to write anomaly log.")


@app.post("/api/detect")
def detect_anomaly(payload: LogFeatures):
    if not all([scaler, label_encoder, model_iso, model_rf, model_features]):
        raise HTTPException(status_code=503, detail="ML models not loaded. Train and restart service.")

    # Convert incoming to DF
    raw = pd.DataFrame([payload.dict()])
    # Align features
    try:
        X_aligned = preprocess_security_logs(raw, expected_features=model_features)
    except Exception as e:
        log.exception("Failed to preprocess incoming features: %s", e)
        raise HTTPException(status_code=400, detail=f"Preprocessing error: {e}")

    # Scale
    try:
        X_scaled = scaler.transform(X_aligned)
    except Exception as e:
        log.exception("Scaling failed: %s", e)
        raise HTTPException(status_code=500, detail="Scaling error")

    # Stage 1: IsolationForest
    iso_pred = model_iso.predict(X_scaled)[0]           # -1 anomaly, 1 normal
    iso_score = float(model_iso.decision_function(X_scaled)[0])
    is_anomaly = (iso_pred == -1)

    # Stage 2: Classification (only necessary if anomaly)
    if is_anomaly:
        rf_pred_enc = int(model_rf.predict(X_scaled)[0])
        try:
            attack_label = label_encoder.inverse_transform([rf_pred_enc])[0]
        except Exception:
            # fallback: if label encoder doesn't map properly
            attack_label = str(rf_pred_enc)
    else:
        # Try to return human 'Normal' if present
        try:
            if "Normal" in label_encoder.classes_:
                attack_label = "Normal"
            else:
                attack_label = label_encoder.inverse_transform([0])[0]
        except Exception:
            attack_label = "Normal"

    # Build response
    response = {
        "node_id": payload.node_id,
        "cloud_provider": payload.cloud_provider,
        "timestamp": payload.timestamp,
        "is_anomaly": bool(is_anomaly),
        "anomaly_score": round(iso_score, 6),
        "attack_type_classified": attack_label
    }

    # Logging the anomaly event to local log file (JSON Lines)
    if response["is_anomaly"]:
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "node_id": response["node_id"],
            "cloud_provider": response["cloud_provider"],
            "anomaly_score": response["anomaly_score"],
            "attack_type": response["attack_type_classified"],
            "raw_event_sample": raw.iloc[0].to_dict()
        }
        append_anomaly_log(log_entry)
        log.warning("Anomaly detected: %s", json.dumps(log_entry, default=str))

        # If the attack is not "Normal", write to forensic ledger and attach its result to response
        if response["attack_type_classified"] != "Normal":
            try:
                ledger_res = log_incident_to_ledger(log_entry, action="AUTOMATED_CONTAINMENT")
                response["forensic_ledger"] = ledger_res
                log.critical("Forensic ledger entry created: %s", str(ledger_res.get("current_hash", "")[:12]))
            except Exception:
                log.exception("Failed to write to forensic ledger; continuing without ledger result.")
                response["forensic_ledger"] = {"error": "ledger_write_failed"}

    return response


@app.get("/health/es")
def health_es():
    """Check elasticsearch connectivity if client available."""
    if Elasticsearch is None:
        raise HTTPException(status_code=501, detail="Elasticsearch client not installed in this environment.")

    try:
        es = Elasticsearch([ES_HOST]) if (ES_HOST := os.getenv("ELASTICSEARCH_HOSTS", None)) else Elasticsearch()
        if not es.ping():
            raise HTTPException(status_code=503, detail="Elasticsearch ping failed.")
        info = es.info()
        return {"status": "ok", "cluster_name": info.get("cluster_name", "")}
    except HTTPException:
        raise
    except Exception as e:
        log.exception("Elasticsearch health check failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "error", "detail": "Elasticsearch health check failed."}
    