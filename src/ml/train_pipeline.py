"""
train_pipeline.py

Trains the two-stage pipeline:
 - Stage 1: IsolationForest (anomaly detection)
 - Stage 2: RandomForestClassifier (attack classification)

Saves a single joblib file containing:
  { "scaler": ..., "label_encoder": ..., "model_iso": ..., "model_rf": ..., "features": [...] }

Run:
$ python -m src.ml.train_pipeline
"""
import os
import logging
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("train_pipeline")

# Configurable paths
DATA_DIR = os.getenv("HG_DATA_DIR", "data/processed/unsw")
X_TRAIN_PATH = os.path.join(DATA_DIR, "X_train.csv")
X_TEST_PATH = os.path.join(DATA_DIR, "X_test.csv")
Y_TRAIN_PATH = os.path.join(DATA_DIR, "y_train_multi_class.csv")
Y_TEST_PATH = os.path.join(DATA_DIR, "y_test_multi_class.csv")

OUTPUT_MODEL = os.getenv("HG_MODEL_PATH", "src/ml/hawkgrid_pipeline.joblib")
MODELS_DIR = os.path.dirname(OUTPUT_MODEL)
os.makedirs(MODELS_DIR, exist_ok=True)

RANDOM_STATE = 42
CONTAMINATION_RATE = float(os.getenv("HG_CONTAMINATION", 0.05))

def load_csv(path: str, is_label: bool = False):
    if not os.path.exists(path):
        log.error("Missing file: %s", path)
        raise FileNotFoundError(path)
    if is_label:
        df = pd.read_csv(path, header=None)
        return df.values.ravel()
    # Always treat as numeric CSVs with no header row
    df = pd.read_csv(path, header=None)
    df.columns = [f"f_{i}" for i in range(df.shape[1])]
    return df


def main():
    log.info("Loading data...")
    X_train = load_csv(X_TRAIN_PATH)
    X_test = load_csv(X_TEST_PATH)
    y_train = load_csv(Y_TRAIN_PATH, is_label=True)
    y_test = load_csv(Y_TEST_PATH, is_label=True)

    # If X_train has no column names, generate generic ones and keep consistent features list
    FEATURES = X_train.columns.tolist()
    log.info("Number of features: %d", len(FEATURES))

    # Fit scaler and label encoder
    log.info("Fitting scaler and label encoder...")
    scaler = StandardScaler().fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    label_encoder = LabelEncoder().fit(y_train)
    
    y_train_enc = label_encoder.transform(y_train)
    y_test_enc = label_encoder.transform(y_test)

    log.info("Training IsolationForest (Stage 1 - anomaly detection)...")
    iso = IsolationForest(n_estimators=100, contamination=CONTAMINATION_RATE, random_state=RANDOM_STATE, n_jobs=-1)
    iso.fit(X_train_scaled)
    log.info("IsolationForest trained.")

    log.info("Training RandomForestClassifier (Stage 2 - attack classification)...")
    rf = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE, n_jobs=-1)
    rf.fit(X_train_scaled, y_train_enc)
    log.info("RandomForest trained.")

    # Evaluate classifier on test set
    log.info("Evaluating classifier on test set...")
    y_pred_enc = rf.predict(X_test_scaled)
    y_pred_labels = label_encoder.inverse_transform(y_pred_enc)

    acc = accuracy_score(y_test, y_pred_labels)
    log.info("Test accuracy: %.4f", acc)
    log.info("Classification report:\n%s", classification_report(y_test, y_pred_labels, zero_division=0))

    # Persist everything in a single joblib
    log.info("Saving pipeline to %s", OUTPUT_MODEL)
    artifacts = {
        "scaler": scaler,
        "label_encoder": label_encoder,
        "model_iso": iso,
        "model_rf": rf,
        "features": FEATURES
    }
    joblib.dump(artifacts, OUTPUT_MODEL)
    log.info("Saved pipeline successfully.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.exception("Training pipeline failed: %s", exc)
        raise
