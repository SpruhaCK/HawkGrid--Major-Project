import joblib
import numpy as np
import pandas as pd
from src.ml.preprocess import preprocess_security_logs
from src.orchestrator.attack_mapper import map_attack_type # Import your rules

MODEL_PATH = "src/ml/hawkgrid_pipeline.joblib"

# Load ML artifacts
_artifacts = joblib.load(MODEL_PATH)
scaler = _artifacts["scaler"]
iso = _artifacts["model_iso"]
features = _artifacts["features"]

def detect_event(raw_df: pd.DataFrame):
    # Preprocess and scale
    aligned = preprocess_security_logs(raw_df, features)
    scaled = scaler.transform(aligned)

    # Step 1: ML Anomaly Detection
    iso_pred = iso.predict(scaled)[0] # -1 = anomaly
    iso_score = float(abs(iso.decision_function(scaled)[0]))

    event_dict = raw_df.iloc[0].to_dict()
    is_anomaly = (iso_pred == -1) 
    
    if is_anomaly:
        # Step 2: Pass to the smarter mapper we fixed earlier
        attack = map_attack_type(event_dict)
        return {
            "is_anomaly": True,
            "anomaly_score": iso_score,
            "attack_type": attack
        }

    return {"is_anomaly": False, "attack_type": "NORMAL"}