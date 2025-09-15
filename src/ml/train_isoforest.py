import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd

df = pd.read_csv("data/processed/X_cicids.csv")
X = df.select_dtypes("number")
scaler = StandardScaler().fit(X)
X_s = scaler.transform(X)
model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42).fit(X_s)
joblib.dump((model, scaler), "models/isolation_forest.joblib")
print("Model saved")