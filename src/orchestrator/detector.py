import joblib
import pandas as pd
from src.ml.preprocess import preprocess_security_logs

MODEL_PATH = "src/ml/hawkgrid_pipeline.joblib"

# Load artifacts
_artifacts = joblib.load(MODEL_PATH)
scaler = _artifacts["scaler"]
iso = _artifacts["model_iso"]
rf = _artifacts["model_rf"]
le = _artifacts["label_encoder"]
features = _artifacts["features"]

UNSW_MAPPING = {
    0.0: "ANALYSIS", 1.0: "BACKDOOR", 2.0: "DOS",
    3.0: "EXPLOITS", 4.0: "FUZZERS", 5.0: "GENERIC",
    6.0: "NORMAL", 7.0: "RECONNAISSANCE", 8.0: "SHELLCODE",
    9.0: "WORMS"
}

def get_owasp_metrics(attack_label: str):
    """Maps classifications to an OWASP Risk Score (1-5) and Severity."""
    mapping = {
        "NORMAL":         {"score": 1, "severity": "LOW", "action": "NONE"},
        "RECONNAISSANCE": {"score": 2, "severity": "MEDIUM", "action": "ALERT_ONLY"},
        "ANALYSIS":       {"score": 3, "severity": "HIGH", "action": "BLOCK_IP"},
        "FUZZERS":        {"score": 3, "severity": "HIGH", "action": "BLOCK_IP"},
        "BRUTE_FORCE":    {"score": 3, "severity": "HIGH", "action": "BLOCK_IP"},
        "GENERIC":        {"score": 3, "severity": "HIGH", "action": "BLOCK_IP"},
        "DOS":            {"score": 4, "severity": "CRITICAL", "action": "AUTOMATED_CONTAINMENT"},
        "BACKDOOR":       {"score": 4, "severity": "CRITICAL", "action": "AUTOMATED_CONTAINMENT"},
        "EXPLOITS":       {"score": 4, "severity": "CRITICAL", "action": "AUTOMATED_CONTAINMENT"},
        "SHELLCODE":      {"score": 5, "severity": "EXTREME", "action": "AUTOMATED_CONTAINMENT"},
        "WORMS":          {"score": 5, "severity": "EXTREME", "action": "AUTOMATED_CONTAINMENT"}
    }
    return mapping.get(attack_label, {"score": 1, "severity": "LOW", "action": "NONE"})

def detect_event(raw_df: pd.DataFrame):
    
    # ---------------------------------------------------------
    # ROUTE 1: LIVE SENSOR (Volumetric Traffic - 3 features)
    # ---------------------------------------------------------
    if "f_0" not in raw_df.columns:
        api_freq = float(raw_df.get("API_Call_Freq", [0])[0])
        failed_auth = float(raw_df.get("Failed_Auth_Count", [0])[0])
        egress = float(raw_df.get("Network_Egress_MB", [0])[0])

        if failed_auth >= 1.0: 
            attack_name = "BRUTE_FORCE" 
        elif api_freq >= 80.0 or egress > 5.0:
            attack_name = "DOS"
        elif api_freq >= 10.0: 
            attack_name = "RECONNAISSANCE"
        else:
            attack_name = "NORMAL"

        metrics = get_owasp_metrics(attack_name)
        
        return {
            "is_anomaly": bool(attack_name != "NORMAL"),
            "anomaly_score": 0.99 if attack_name != "NORMAL" else 0.0,
            "attack_type": attack_name,
            "owasp_risk_score": metrics["score"],
            "severity": metrics["severity"],
            "recommended_action": metrics["action"]
        }

    # ---------------------------------------------------------
    # ROUTE 2: DEEP PACKET INSPECTION (Simulated ML - 44 features)
    # ---------------------------------------------------------
    else:
        aligned = preprocess_security_logs(raw_df, features)
        scaled = scaler.transform(aligned)

        rf_pred_id = rf.predict(scaled)[0]
        numeric_label = le.inverse_transform([rf_pred_id])[0]
        attack_name = UNSW_MAPPING.get(float(numeric_label), "NORMAL")
        
        is_anomaly = bool(attack_name != "NORMAL")
        iso_score = float(abs(iso.decision_function(scaled)[0]))
        metrics = get_owasp_metrics(attack_name)

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": iso_score,
            "attack_type": attack_name,
            "owasp_risk_score": metrics["score"],
            "severity": metrics["severity"],
            "recommended_action": metrics["action"]
        }