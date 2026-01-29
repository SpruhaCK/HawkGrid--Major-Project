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


# def preprocess_security_logs(raw_df: pd.DataFrame, expected_features: List[str]) -> pd.DataFrame:
#     """
#     Aligns incoming live logs (raw_df) to the expected features used during training.
    
#     This function handles the critical mismatch between simulation feature names
#     (e.g., 'Network_Egress_MB') and the model's trained feature names (e.g., 'f_0' or 'dbytes').
    
#     It assumes the *order* of the numeric features in the simulation
#     matches the *order* of the features the model was trained on.
#     """
#     df = raw_df.copy(deep=True)
    
#     # --- BEGIN FIX ---
    
#     # 1. Get the list of feature names the *model* expects (e.g., ['f_0', 'f_1', 'f_2', ...])
#     model_feature_names = [str(f) for f in expected_features]
    
#     # 2. Get the list of *numeric* feature names from the *simulation*
#     #    (e.g., ['Network_Egress_MB', 'API_Call_Freq', 'Failed_Auth_Count'])
#     sim_numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()

#     # 3. Create the mapping for *only* the features we can map
#     #    This is the core of the fix. We map the first N sim features
#     #    to the first N model features.
    
#     num_to_map = min(len(sim_numeric_features), len(model_feature_names))
#     if num_to_map == 0:
#         log.warning("No numeric features found in simulation data.")
#         # Proceed, which will create a zero vector later
    
#     sim_features_to_map = sim_numeric_features[:num_to_map]
#     model_features_to_map = model_feature_names[:num_to_map]
    
#     # 4. Create the rename map
#     #    (e.g., {'Network_Egress_MB': 'f_0', 'API_Call_Freq': 'f_1', 'Failed_Auth_Count': 'f_2'})
#     try:
#         rename_map = dict(zip(sim_features_to_map, model_features_to_map))
#         df.rename(columns=rename_map, inplace=True)
#         log.debug(f"Successfully mapped sim features to model features: {rename_map}")
#     except Exception as e:
#         log.exception(f"Failed to create feature rename map: {e}")
#         # Fallback to an empty df, which will be zero-padded
#         df = pd.DataFrame()

#     # --- END FIX ---

#     # 5. Now, use the original alignment logic.
#     #    This creates the full-width DataFrame the model expects.
#     aligned = pd.DataFrame(columns=model_feature_names, index=df.index)
    
#     for col in model_feature_names:
#         if col in df.columns:
#             # Copy the *real data* from the sim (now renamed)
#             aligned[col] = df[col]
#         else:
#             # Pad all *other* features (e.g., f_3 to f_40) with 0.0
#             aligned[col] = 0.0

#     # 6. Ensure numeric dtype and fill NaNs
#     for col in aligned.columns:
#         aligned[col] = pd.to_numeric(aligned[col], errors="coerce").fillna(0.0)

#     # Final sanity: shape and return
#     log.debug(f"preprocess_security_logs -> aligned shape: {aligned.shape}")
#     return aligned

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