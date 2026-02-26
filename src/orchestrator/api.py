import sys
import os
import json 
import logging
import joblib
import boto3
import pandas as pd
from typing import Optional, List
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ConfigDict

# Azure imports
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential

# --- PATH SETUP ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# --- LOCAL IMPORTS ---
from src.orchestrator.detector import detect_event
from src.orchestrator.report_writer import append_report

# --- CONFIG & LOGGING ---
MODEL_PATH = os.getenv("HG_MODEL_PATH", "src/ml/hawkgrid_pipeline.joblib")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("hawkgrid-api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        data = joblib.load(MODEL_PATH)
        app.state.scaler = data["scaler"]
        app.state.model_iso = data["model_iso"]
        log.info("ML models loaded.")
    except Exception as e:
        log.error(f"ML Load Failed: {e}")
    
    app.state.azure_client = LogsQueryClient(DefaultAzureCredential())
    yield

app = FastAPI(title="HawkGrid Core", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class LogFeatures(BaseModel):
    model_config = ConfigDict(extra="allow")
    dst_ip: str
    src_ip: str
    rate: float = 0.0
    sttl: float = 0.0
    sbytes: float = 0.0
    API_Call_Freq: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# =========================
# ROUTES
# =========================

@app.post("/api/detect")
def detect_anomaly(payload: LogFeatures):
    try:
        raw_dict = payload.model_dump()
        raw_df = pd.DataFrame([raw_dict])
        
        detection = detect_event(raw_df, app.state.model_iso, app.state.scaler) 
        
        report_data = {
            "raw_event": raw_dict,
            "detection": detection,
            "response": {"action": "AUTOMATED_CONTAINMENT" if detection["is_anomaly"] else "NONE"}
        }
        
        append_report(report_data)
        return {"status": "processed", "anomaly": detection["is_anomaly"], "type": detection["attack_type"]}
    except Exception as e:
        log.error(f"API Route Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/download-logs")
async def download_logs():
    """Endpoint for the local laptop to download the latest forensic log."""
    log_path = os.path.join(ROOT_DIR, "reports", "forensic_audit.json")
    if os.path.exists(log_path):
        return FileResponse(
            path=log_path, 
            filename="forensic_audit.json", 
            media_type="application/json"
        )
    return {"error": "File not found"}

@app.get("/status")
def status():
    return {"status": "HawkGrid Online"}

if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0" is critical to allow external connections from your PC
    uvicorn.run(app, host="0.0.0.0", port=8000)