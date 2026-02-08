"""
preprocess.py

Provides:
- build_preprocessing_tools(...)  -> fits & saves scaler, label encoder, feature metadata
- preprocess_security_logs(df, expected_features) -> aligns a live DataFrame to expected features

Usage (CLI):
$ python -m src.ml.preprocess
This will look for training CSVs in data/processed/unsw/ and create scaler/label_encoder/features in src/ml/models/
"""
import os
import joblib
import logging
from typing import List, Union, Dict, Any
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("preprocess")

# Default locations (change if you prefer)
DATA_DIR = os.getenv("HG_DATA_DIR", "data/processed/unsw")
X_TRAIN_PATH = os.path.join(DATA_DIR, "X_train.csv")
Y_TRAIN_PATH = os.path.join(DATA_DIR, "y_train_multi_class.csv")

MODELS_DIR = os.getenv("HG_MODELS_DIR", "src/ml/models")
os.makedirs(MODELS_DIR, exist_ok=True)

SCALER_PATH = os.path.join(MODELS_DIR, "scaler.joblib")
ENCODER_PATH = os.path.join(MODELS_DIR, "label_encoder.joblib")
FEATURES_PATH = os.path.join(MODELS_DIR, "features.joblib")


def build_preprocessing_tools(x_train_path: str = X_TRAIN_PATH, y_train_path: str = Y_TRAIN_PATH):
    """
    Fits a StandardScaler and LabelEncoder on the provided train CSVs and saves the artifacts.
    Saves:
      - scaler.joblib
      - label_encoder.joblib
      - features.joblib (list of column names OR number of features)
    """
    from sklearn.preprocessing import StandardScaler, LabelEncoder

    log.info("Building preprocessing tools...")
    if not os.path.exists(x_train_path) or not os.path.exists(y_train_path):
        log.error("Train files not found. Make sure X_train.csv and y_train_multi_class.csv exist under data/processed/unsw/")
        raise FileNotFoundError("Training CSVs missing.")

    # Attempt to load CSVs. We support both header/no-header cases.
    try:
        X = pd.read_csv(x_train_path, header=0)
    except Exception:
        # Fallback to header=None (old UNSW CSVs sometimes don't have headers)
        X = pd.read_csv(x_train_path, header=None)
        # if header=None, create generic names
        X.columns = [f"f_{i}" for i in range(X.shape[1])]

    y = pd.read_csv(y_train_path, header=None).values.ravel()

    # Fit scaler & encoder
    scaler = StandardScaler().fit(X)
    le = LabelEncoder().fit(y)

    # Save artifacts
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(le, ENCODER_PATH)

    # Save feature list (important: keep column names order)
    features = X.columns.tolist()
    joblib.dump(features, FEATURES_PATH)

    log.info(f"Saved scaler -> {SCALER_PATH}")
    log.info(f"Saved label encoder -> {ENCODER_PATH}")
    log.info(f"Saved features ({len(features)}) -> {FEATURES_PATH}")

    return {"scaler": SCALER_PATH, "label_encoder": ENCODER_PATH, "features": FEATURES_PATH}

def preprocess_security_logs(raw_df: pd.DataFrame, expected_features: List[str]) -> pd.DataFrame:
    df = raw_df.copy(deep=True)
    
    # --- ACCURACY FIX: Explicit Mapping to UNSW Features ---
    # We map our simulation variables to the specific UNSW features 
    # that the Isolation Forest recognizes as "Attack Indicators"
    mapping = {
        "API_Call_Freq": "rate",
        "Failed_Auth_Count": "sttl",
        "Network_Egress_MB": "sbytes"
    }
    
    # Rename the columns if they exist in the incoming data
    df = df.rename(columns=mapping)
    
    # Initialize a blank DataFrame with ALL features the model expects (e.g., all 44 columns)
    aligned = pd.DataFrame(0.0, index=df.index, columns=expected_features)
    
    # Fill in the features we actually have data for
    for col in expected_features:
        if col in df.columns:
            aligned[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    log.info(f"Feature alignment complete. Mapped: {list(df.columns)} to model features.")
    return aligned


if __name__ == "__main__":
    # CLI entry: build preprocessing tools from default paths
    try:
        build_preprocessing_tools()
        log.info("Preprocessing artifacts created successfully.")
    except Exception as e:
        log.exception("Failed to create preprocessing tools: {s}", e)
        raise