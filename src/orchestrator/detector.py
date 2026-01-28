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
    """
    Hybrid Detection:
    1. ML (Isolation Forest) detects IF an event is an anomaly.
    2. Rules (Attack Mapper) classify WHAT kind of attack it is.
    """
    # Preprocess and scale
    aligned = preprocess_security_logs(raw_df, features)
    scaled = scaler.transform(aligned)

    # Step 1: Unsupervised Anomaly Detection
    iso_pred = iso.predict(scaled)[0]      # -1 = anomaly, 1 = normal
    iso_score = iso.decision_function(scaled)[0]

    # Convert dataframe row back to a dictionary for the rule-mapper
    event_dict = raw_df.iloc[0].to_dict()

    if iso_pred == -1:
        # Step 2: Use Rule-Based Mapper for precise labels
        attack = map_attack_type(event_dict)
        
        return {
            "is_anomaly": True,
            "anomaly_score": float(abs(iso_score)),
            "attack_type": attack
        }

    return {
        "is_anomaly": False,
        "anomaly_score": float(abs(iso_score)),
        "attack_type": "NORMAL"
    }