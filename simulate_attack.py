"""
simulate_attack.py

"Red Team" simulation script for HawkGrid.
This script sends a variety of mock log entries (both benign and malicious)
to the running HawkGrid API server to test its detection and response.

This file is intended to be run from your local machine, *outside* Docker.

Make sure to install dependencies:
pip install -r requirements-sim.txt
"""

import requests
import json
import time
import random

# --- CONFIG ---
API_URL = "http://localhost:8000/api/detect"
HEADERS = {"Content-Type": "application/json"}
LOOP_DELAY = 10 # Seconds to wait before restarting simulation cycle
# --- END CONFIG ---

def print_header(title):
    print("\n" + ("-" * 3) + f" SIMULATING: {title} " + ("-" * 3))

def print_result(response_json):
    """Pretty-prints the API's JSON response and our analysis."""
    print("API Response: " + json.dumps(response_json, indent=2))
    
    # Analyze the response
    is_anomaly = response_json.get("is_anomaly", False)
    attack_type = response_json.get("attack_type_classified", "N/A")
    
    if is_anomaly:
        print(f"\n>>> [!!] DETECTION: Anomaly classified as '{attack_type}'")
    else:
        print("\n>>> [OK] DETECTION: Traffic classified as Normal.")

    # Check ledger status
    ledger_status = response_json.get("forensic_ledger", {})
    
    # --- THIS IS THE FIX ---
    # Check if the 'error' key exists, otherwise check for a hash
    if ledger_status and "error" in ledger_status:
        print(f">>> [!!] LEDGER: Write FAILED. Status: {ledger_status.get('error')}")
    elif ledger_status:
        # It's a successful local-file log
        hash_val = ledger_status.get('current_hash', 'unknown_hash')[:12]
        print(f">>> [OK] LEDGER: Wrote to ledger. Hash: {hash_val}...")
    else:
        # Not an anomaly, so no ledger write was attempted.
        pass # No need to print anything

    # Check response status
    response_status = response_json.get("incident_response", {})
    if response_status:
        status = response_status.get('status', 'unknown')
        if "fail" in status:
            print(f">>> [!!] RESPONSE: Playbook status: {status}")
        else:
            print(f">>> [OK] RESPONSE: Playbook status: {status}")


def send_log(payload: dict, title: str):
    """Sends a single log payload to the API and prints the result."""
    print_header(title)
    print("Sending payload: " + json.dumps(payload))
    
    try:
        response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for 4xx/5xx errors
        
        print_result(response.json())

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Connection refused. Is the Docker container running?")
        print("Please run: docker-compose up --build")
    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] HTTP Error: {e.response.status_code}")
        print(f"Details: {e.response.text}")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")

# --- SIMULATION SCENARIOS ---

def simulate_normal_traffic():
    """Simulate a benign user just browsing."""
    payload = {
        # Randomize normal traffic to avoid caching
        "Network_Egress_MB": random.uniform(5.0, 20.0),
        "API_Call_Freq": random.uniform(10.0, 50.0),
        "Failed_Auth_Count": 0.0,
        "node_id": "AWS-EC2-B",
        "cloud_provider": "aws",
        "description": "Simulating normal user traffic"
    }
    send_log(payload, "Normal Traffic (Expect: No Anomaly)")

def simulate_data_exfiltration():
    """Simulate a compromised node sending out a large amount of data."""
    payload = {
        "Network_Egress_MB": 950.0, # Very high egress
        "API_Call_Freq": 25.0,
        "Failed_Auth_Count": 0.0,
        "node_id": "AWS-EC2-B",
        "cloud_provider": "aws",
        "description": "Simulating data exfiltration"
    }
    send_log(payload, "Data Exfiltration (Expect: Anomaly, Containment)")

def simulate_brute_force():
    """Simulate a brute-force login attack."""
    payload = {
        "Network_Egress_MB": 2.0,
        "API_Call_Freq": 150.0,
        "Failed_Auth_Count": 120.0, # Very high auth failures
        "node_id": "Azure-VM-A",
        "cloud_provider": "azure",
        "description": "Simulating a brute force login attack"
    }
    send_log(payload, "Brute Force Attack (Expect: Anomaly, Containment)")

def simulate_c2_beaconing():
    """Simulate a C2 beacon from an unknown node."""
    payload = {
        "Network_Egress_MB": 0.5,
        "API_Call_Freq": 100.0,
        "Failed_Auth_Count": 0.0,
        "node_id": "unknown-node-123", # Not in our asset DB
        "cloud_provider": "gcp",
        "description": "Simulating C2 beaconing"
    }
    send_log(payload, "C2 Beaconing (Expect: Anomaly, Response Failure - Unknown Node)")

# --- MAIN EXECUTION ---

def main():
    print("=" * 44)
    print("==    HawkGrid Red Team Simulation Start    ==")
    print("=" * 44)
    print(f"Targeting API: {API_URL}\n")
    print("Please ensure the HawkGrid Docker container is running.")
    try:
        input("Press Enter to begin...")
    except KeyboardInterrupt:
        return

    while True:
        try:
            simulate_normal_traffic()
            time.sleep(1)
            
            simulate_data_exfiltration()
            time.sleep(1)

            simulate_brute_force()
            time.sleep(1)

            simulate_c2_beaconing()
            
            print("\n" + "=" * 44)
            print("==    Simulation cycle complete.        ==")
            print(f"==    Restarting in {LOOP_DELAY} seconds...        ==")
            print("==    (Press Ctrl+C to stop)            ==")
            print("=" * 44)
            time.sleep(LOOP_DELAY)

        except KeyboardInterrupt:
            print("\nSimulation stopped by user.")
            break
        except Exception as e:
            print(f"\n[FATAL] Simulation loop crashed: {e}")
            print("Restarting in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    main()