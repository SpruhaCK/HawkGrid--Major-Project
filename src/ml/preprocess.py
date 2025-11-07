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


def preprocess_security_logs(raw_df: pd.DataFrame, expected_features: Union[List[str], int, Dict[str, Any]]):
    """
    Aligns incoming live logs (raw_df) to the expected features used during training.
    - expected_features: either a list of column names (preferred), OR an integer number of features.
    - Returns a DataFrame containing only numeric columns in the same order as expected_features.
    - Missing features are added with zeros; extra columns in raw_df are ignored.

    This function never mutates raw_df in-place.
    """
    df = raw_df.copy(deep=True)
    # Convert column names to string to avoid dtype mismatch
    df.columns = [str(c) for c in df.columns]

    # If expected_features is a dict (metadata), try to extract list or number
    if isinstance(expected_features, dict):
        if "num_features" in expected_features:
            expected = int(expected_features["num_features"])
        elif "features" in expected_features:
            expected = list(expected_features["features"])
        else:
            raise ValueError("Unsupported features metadata dict. Provide 'features' (list) or 'num_features' (int).")
    else:
        expected = expected_features

    # Case A: expected is a list of column names
    if isinstance(expected, list):
        target_cols = [str(c) for c in expected]

        # For columns missing in incoming data, add zeros
        for c in target_cols:
            if c not in df.columns:
                df[c] = 0.0

        # Keep only target columns in the exact order
        aligned = df[target_cols].copy()

    # Case B: expected is an integer (number of features)
    elif isinstance(expected, int):
        n = expected
        # If incoming df has fewer numeric columns, pad with zeros
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= n:
            aligned = df[numeric_cols[:n]].copy()
        else:
            # take all numeric columns and pad additional columns with zeros
            aligned = df[numeric_cols].copy()
            for i in range(n - len(numeric_cols)):
                aligned[f"pad_{i}"] = 0.0
            # reorder to a deterministic order
            aligned = aligned[[*numeric_cols, *[f"pad_{i}" for i in range(n - len(numeric_cols))]]]
    else:
        raise ValueError("expected_features must be a list or int or dict containing them.")

    # Ensure numeric dtype and fill NaNs
    for col in aligned.columns:
        aligned[col] = pd.to_numeric(aligned[col], errors="coerce").fillna(0.0)

    # Final sanity: shape and return
    log.debug(f"preprocess_security_logs -> aligned shape: {aligned.shape}")
    return aligned


if __name__ == "__main__":
    # CLI entry: build preprocessing tools from default paths
    try:
        build_preprocessing_tools()
        log.info("Preprocessing artifacts created successfully.")
    except Exception as e:
        log.exception("Failed to create preprocessing tools: %s", e)
        raise
