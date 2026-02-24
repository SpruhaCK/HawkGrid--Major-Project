import os
import time
import requests
import pandas as pd
import random

# Use the data you uploaded
X_TEST_PATH = "data/processed/unsw/X_test.csv"
Y_TEST_PATH = "data/processed/unsw/y_test_multi_class.csv"
API_URL = "http://127.0.0.1:8000/api/detect"

UNSW_MAPPING = {
    0.0: "ANALYSIS (OWASP Web/Traversal)",
    1.0: "BACKDOOR (Persistence)",
    2.0: "DOS",
    3.0: "EXPLOITS (OWASP Top 10)",
    4.0: "FUZZERS (OWASP Injection)",
    5.0: "GENERIC",
    6.0: "NORMAL",
    7.0: "RECONNAISSANCE (Scanning)",
    8.0: "SHELLCODE (RCE)",
    9.0: "WORMS (Lateral Movement)"
}

def simulate_attacks():
    print("Loading test dataset features and labels...")
    # Load data without headers
    x_test = pd.read_csv(X_TEST_PATH, header=None)
    y_test = pd.read_csv(Y_TEST_PATH, header=None)

    # Name features f_0 to f_43 to match your training script
    x_test.columns = [f"f_{i}" for i in range(x_test.shape[1])]

    print("\n--- HAWKGRID ADVANCED ATTACK SIMULATOR ---")
    print("Simulating payloads with all 44 complex network features.\n")

    for _ in range(10): # Simulate 10 random packets
        idx = random.randint(0, len(x_test) - 1)
        
        # Get the actual label from the CSV
        actual_label_num = float(y_test.iloc[idx, 0])
        actual_name = UNSW_MAPPING.get(actual_label_num, "UNKNOWN")

        # Convert the row to a dictionary
        payload = x_test.iloc[idx].to_dict()
        
        # Add the required base fields for the API
        payload["dst_ip"] = "13.222.116.238"  # Your AWS target
        payload["src_ip"] = f"192.168.1.{random.randint(10, 200)}" # Spoofed attacker

        print(f"[*] Sending Payload... True Category: {actual_name}")
        
        try:
            resp = requests.post(API_URL, json=payload, timeout=5)
            result = resp.json()
            
            detected_as = result["detection"]["attack_type"]
            score = result["detection"]["owasp_risk_score"]
            action = result["response"]["action"]
            
            print(f"    -> API Detected: {detected_as} | Risk Score: {score}/5 | Action Triggered: {action}\n")
        except Exception as e:
            print(f"    -> Failed to reach API: {e}")
            
        time.sleep(2)

if __name__ == "__main__":
    simulate_attacks()