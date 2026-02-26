# import os
# import time
# import requests
# import pandas as pd
# import random
# import logging
# from dotenv import load_dotenv

# # 🚨 BULLETPROOF .ENV LOADER
# current_dir = os.path.dirname(os.path.abspath(__file__))
# env_path = os.path.join(current_dir, '.env')
# load_dotenv(dotenv_path=env_path, override=True)

# from src.cloud.provider_factory import get_cloud_providers

# logging.getLogger("hawkgrid-provider").setLevel(logging.WARNING)
# logging.getLogger("azure_provider").setLevel(logging.WARNING)

# X_TEST_PATH = "data/processed/unsw/X_test.csv"
# Y_TEST_PATH = "data/processed/unsw/y_test_multi_class.csv"
# API_URL = "http://127.0.0.1:8000/api/detect"

# UNSW_MAPPING = {
#     0.0: "ANALYSIS (Traversal/Probing)",
#     1.0: "BACKDOOR (Persistence)",
#     2.0: "DOS (Denial of Service)",
#     3.0: "EXPLOITS (Software Vulnerabilities)",
#     4.0: "FUZZERS (Payload Injection)",
#     5.0: "GENERIC (Cryptographic/Block)",
#     6.0: "NORMAL (Benign Traffic)",
#     7.0: "RECONNAISSANCE (Port Scanning)",
#     8.0: "SHELLCODE (Remote Command Execution)",
#     9.0: "WORMS (Lateral Movement)"
# }

# def get_dynamic_target_ips():
#     print("[*] Contacting Cloud Providers to discover live IPs...")
#     providers = get_cloud_providers()
#     live_ips = []
#     for name, provider in providers.items():
#         try:
#             assets = provider.discover_assets()
#             for asset in assets:
#                 ip = asset.get("public_ip")
#                 if ip:
#                     live_ips.append(ip)
#                     print(f"    -> Found {name.upper()} IP: {ip}")
#         except Exception as e:
#             print(f"    -> Error loading {name} assets: {e}")
            
#     if not live_ips:
#         print("[!] No live cloud IPs found! Defaulting to localhost.")
#         live_ips = ["127.0.0.1"]
#     return live_ips

# def simulate_attacks():
#     target_ips = get_dynamic_target_ips()
    
#     print("\nLoading test dataset features and labels...")
#     x_test = pd.read_csv(X_TEST_PATH, header=None)
#     y_test = pd.read_csv(Y_TEST_PATH, header=None)
#     x_test.columns = [f"f_{i}" for i in range(x_test.shape[1])]

#     print("\n--- HAWKGRID ADVANCED ATTACK SIMULATOR ---")
#     print("Mode: GUARANTEED COVERAGE (One of each attack type)\n")

#     # 🚨 NEW LOGIC: Loop through every attack category (0 to 9)
#     for category_num in range(10):
#         category_float = float(category_num)
#         attack_name = UNSW_MAPPING.get(category_float, "UNKNOWN")
        
#         # Find all rows in the dataset that match this specific attack
#         matching_indices = y_test.index[y_test[0] == category_float].tolist()
        
#         if not matching_indices:
#             print(f"[!] Warning: No examples of {attack_name} found in dataset.")
#             continue
            
#         # Pick one random example from this specific class
#         idx = random.choice(matching_indices)
        
#         payload = x_test.iloc[idx].to_dict()
#         payload["dst_ip"] = random.choice(target_ips) 
#         payload["src_ip"] = f"192.168.1.{random.randint(10, 200)}" 

#         print(f"[*] Sending Payload to {payload['dst_ip']}... True Category: {attack_name}")
        
#         try:
#             resp = requests.post(API_URL, json=payload, timeout=5)
#             result = resp.json()
            
#             detected_as = result.get("detection", {}).get("attack_type", "UNKNOWN")
#             score = result.get("detection", {}).get("owasp_risk_score", 0)
            
#             action = "NONE"
#             if "response" in result and "action" in result["response"]:
#                 action = result["response"]["action"]
#             elif "recommended_action" in result.get("detection", {}):
#                 action = result["detection"]["recommended_action"]
            
#             print(f"    -> API Detected: {detected_as} | Risk Score: {score}/5 | Action Triggered: {action}\n")
#         except Exception as e:
#             print(f"    -> Failed to reach API: {e}")
            
#         time.sleep(1.5)

# if __name__ == "__main__":
#     simulate_attacks()

import os
import time
import requests
import pandas as pd
import random
import logging
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=env_path, override=True)

from src.cloud.provider_factory import get_cloud_providers

logging.getLogger("hawkgrid-provider").setLevel(logging.WARNING)
logging.getLogger("azure_provider").setLevel(logging.WARNING)

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

def get_dynamic_target_ips():
    print("[*] Contacting Cloud Providers to discover live IPs...")
    providers = get_cloud_providers()
    live_ips = []
    for name, provider in providers.items():
        try:
            assets = provider.discover_assets()
            for asset in assets:
                ip = asset.get("public_ip")
                if ip:
                    live_ips.append(ip)
                    print(f"    -> Found {name.upper()} IP: {ip}")
        except Exception as e:
            print(f"    -> Error loading {name} assets: {e}")
            
    if not live_ips:
        print("[!] No live cloud IPs found! Defaulting to localhost.")
        live_ips = ["127.0.0.1"]
    return live_ips

def simulate_attacks():
    target_ips = get_dynamic_target_ips()
    
    print("\nLoading test dataset features and labels...")
    x_test = pd.read_csv(X_TEST_PATH, header=None)
    y_test = pd.read_csv(Y_TEST_PATH, header=None)
    x_test.columns = [f"f_{i}" for i in range(x_test.shape[1])]

    print("\n--- HAWKGRID ADVANCED ATTACK SIMULATOR ---")
    print("Mode: GUARANTEED COVERAGE (One of each attack type)\n")

    for category_num in range(10):
        category_float = float(category_num)
        attack_name = UNSW_MAPPING.get(category_float, "UNKNOWN")
        
        matching_indices = y_test.index[y_test[0] == category_float].tolist()
        
        if not matching_indices:
            print(f"[!] Warning: No examples of {attack_name} found in dataset.")
            continue
            
        idx = random.choice(matching_indices)
        
        payload = x_test.iloc[idx].to_dict()
        payload["dst_ip"] = random.choice(target_ips) 
        payload["src_ip"] = f"192.168.1.{random.randint(10, 200)}" 

        # =========================================================
        # 🚨 FOR LATERAL MOVEMENT DEMO (AWS Windows -> AWS Ubuntu)
        # Uncomment the two lines below and add your real public IPs
        # =========================================================
        payload["dst_ip"] = "52.90.149.125"
        payload["src_ip"] = "44.214.5.49"

        print(f"[*] Sending Payload to {payload['dst_ip']}... True Category: {attack_name}")
        
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
            
            print(f"    -> API Detected: {detected_as} | Risk Score: {score}/5 | Action Triggered: {action}\n")
        except Exception as e:
            print(f"    -> Failed to reach API: {e}")
            
        time.sleep(1.5)

if __name__ == "__main__":
    simulate_attacks()