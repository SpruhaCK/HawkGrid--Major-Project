import os
import time
import requests
import pandas as pd
import random

# =====================================================================
# 🎯 MANUAL ROLE ASSIGNMENT FOR DEMO DAY
# =====================================================================

# 🏴‍☠️ 1. THE ROGUE ATTACKER (Cloud Instance)
# Paste the Public IP of the AWS/Azure instance you want to act as the attacker.
# THIS is the IP that the API will detect and block in your cloud firewalls.
ROGUE_ATTACKER_IP = "98.86.166.137"  # Replace with your actual attacker IP

# 🛡️ 2. THE VICTIMS (Cloud Instances)
# Paste the Public IPs of the instances that will be attacked.
# The script will randomly select one of these for each payload.
VICTIM_IPS = [
    "98.84.48.255",   # Example: AWS Victim
    # "20.114.88.99" # Example: Azure Victim (Uncomment when ready)
]

# =====================================================================
# SYSTEM CONFIG
# =====================================================================
X_TEST_PATH = "data/processed/unsw/X_test.csv"
Y_TEST_PATH = "data/processed/unsw/y_test_multi_class.csv"
API_URL = "http://127.0.0.1:8000/api/detect"

UNSW_MAPPING = {
    0.0: "ANALYSIS (Traversal/Probing)",
    1.0: "BACKDOOR (Persistence)",
    2.0: "DOS (Denial of Service)",
    3.0: "EXPLOITS (Software Vulnerabilities)",
    4.0: "FUZZERS (Payload Injection)",
    5.0: "GENERIC (Cryptographic/Block)",
    6.0: "NORMAL (Benign Traffic)",
    7.0: "RECONNAISSANCE (Port Scanning)",
    8.0: "SHELLCODE (Remote Command Execution)",
    9.0: "WORMS (Lateral Movement)"
}

def simulate_attacks():
    if not os.path.exists(X_TEST_PATH) or not os.path.exists(Y_TEST_PATH):
        print(f"\n[!] CRITICAL ERROR: Dataset files not found in data/processed/unsw/")
        return

    print("\nLoading test dataset features and labels...")
    x_test = pd.read_csv(X_TEST_PATH, header=None)
    y_test = pd.read_csv(Y_TEST_PATH, header=None)
    x_test.columns = [f"f_{i}" for i in range(x_test.shape[1])]

    print("\n=======================================================")
    print("   🦅 HAWKGRID: CLOUD-TO-CLOUD WAR GAMES SIMULATOR")
    print("=======================================================")
    print(f"🏴‍☠️ Attacker Instance IP : {ROGUE_ATTACKER_IP}")
    print(f"🛡️ Victim Instance(s)   : {', '.join(VICTIM_IPS)}")
    print("=======================================================\n")

    for category_num in range(10):
        category_float = float(category_num)
        attack_name = UNSW_MAPPING.get(category_float, "UNKNOWN")
        
        matching_indices = y_test.index[y_test[0] == category_float].tolist()
        if not matching_indices:
            continue
            
        # Pick a random payload from this specific attack category
        idx = random.choice(matching_indices)
        payload = x_test.iloc[idx].to_dict()
        
        # 🚨 OVERRIDE THE IPS WITH YOUR HARDCODED ROLES 🚨
        payload["src_ip"] = ROGUE_ATTACKER_IP
        payload["dst_ip"] = random.choice(VICTIM_IPS)

        print(f"[*] Sending Payload... True Category: {attack_name}")
        print(f"    -> Route: {payload['src_ip']} ===> {payload['dst_ip']}")
        
        try:
            resp = requests.post(API_URL, json=payload, timeout=5)
            result = resp.json()
            
            detected_as = result.get("detection", {}).get("attack_type", "UNKNOWN")
            score = result.get("detection", {}).get("owasp_risk_score", 0)
            
            action = "NONE"
            if "response" in result and "action" in result["response"]:
                action = result["response"]["action"]
            elif "recommended_action" in result.get("detection", {}):
                action = result["detection"]["recommended_action"]
            
            print(f"    -> 🧠 API Detected: {detected_as} | Risk Score: {score}/5")
            print(f"    -> 🛡️ Action Triggered: {action}\n")
            
        except requests.exceptions.ConnectionError:
             print(f"    -> [!] Connection Error: Is your HawkGrid API running on {API_URL}?\n")
        except Exception as e:
            print(f"    -> [!] Failed to reach API: {e}\n")
            
        time.sleep(2)

if __name__ == "__main__":
    if not VICTIM_IPS:
        print("[!] Please add at least one IP to VICTIM_IPS at the top of the script.")
    else:
        simulate_attacks()