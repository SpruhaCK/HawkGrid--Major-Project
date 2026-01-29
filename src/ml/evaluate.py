import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.metrics import confusion_matrix, classification_report

# --- CONFIG ---
MODEL_PATH = "src/ml/hawkgrid_pipeline.joblib"
DATA_DIR = "data/processed/unsw"
X_TEST_PATH = os.path.join(DATA_DIR, "X_test.csv")
Y_TEST_PATH = os.path.join(DATA_DIR, "y_test_multi_class.csv")
LABELS = ['Normal', 'Brute Force', 'DoS/DDoS', 'Port Scan']

def generate_evaluation():
    # 1. Load Model and Data
    print("Loading pipeline and test data...")
    data = joblib.load(MODEL_PATH)
    X_test = pd.read_csv(X_TEST_PATH, header=None)
    y_test = pd.read_csv(Y_TEST_PATH, header=None).values.ravel()

    # 2. Get Predictions
    # We use the RandomForest part of your pipeline for the matrix labels
    scaler = data["scaler"]
    rf_model = data["model_rf"]
    le = data["label_encoder"]
    
    X_test_scaled = scaler.transform(X_test)
    y_pred_enc = rf_model.predict(X_test_scaled)
    y_pred = le.inverse_transform(y_pred_enc)

    # 3. Generate Official Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    
    # 4. Plot using Seaborn (Professional IEEE look)
    plt.figure(figsize=(10, 7))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=le.classes_, yticklabels=le.classes_)
    plt.title('HawkGrid Multi-Cloud Detection: Confusion Matrix')
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    plt.savefig('logs/confusion_matrix.png') # Saves it for your report!
    print("Confusion Matrix saved to logs/confusion_matrix.png")

    # 5. Print Official Classification Report
    print("\n--- IEEE CLASSIFICATION REPORT ---")
    print(classification_report(y_test, y_pred))

if __name__ == "__main__":
    generate_evaluation()