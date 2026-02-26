import pandas as pd
import numpy as np
import logging
from src.orchestrator.attack_mapper import map_attack_type
from datetime import datetime, timezone

def detect_event(raw_df: pd.DataFrame, model, scaler):
    try:
        # 1. Get the number of features the scaler expects
        # This solves the "f_10, f_11 missing" error
        expected_count = scaler.n_features_in_
        
        # 2. Extract our real data
        current_data = raw_df[['rate', 'sttl', 'sbytes', 'API_Call_Freq']].values
        
        # 3. Pad with zeros to match the model's training size
        padded_data = np.zeros((1, expected_count))
        padded_data[0, :4] = current_data[0] 
        
        # 4. Create DataFrame with generic names f_0, f_1...
        features = pd.DataFrame(padded_data, columns=[f'f_{i}' for i in range(expected_count)])

        # 5. Transform and Predict
        scaled_features = scaler.transform(features)
        prediction = model.predict(scaled_features)
        
        try:
            score = model.decision_function(scaled_features)[0]
        except:
            score = 0.99

        attack = map_attack_type(raw_df.iloc[0].to_dict())

        return {
            "is_anomaly": True if prediction[0] == -1 else False,
            "anomaly_score": float(score),
            "attack_type": attack,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logging.error(f"Detection Logic Failed: {e}")
        return {"is_anomaly": True, "attack_type": "EMERGENCY_FALLBACK"}