# sync_logs.py on Laptop
import requests
import os
import time

# CHANGE THIS to the Public IP from Azure Portal
VM_IP = "4.213.51.69" 
URL = f"http://{VM_IP}:8000/api/download-logs"
SAVE_PATH = r"C:\Users\Janhavi\HawkGrid--Major-Project\reports\forensic_audit.json"

print(f"--- HawkGrid Sync: Connecting to {VM_IP} ---")

while True:
    try:
        r = requests.get(URL, timeout=10)
        if r.status_code == 200:
            os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
            with open(SAVE_PATH, "wb") as f:
                f.write(r.content)
            print(f"[{time.strftime('%H:%M:%S')}] Success: Logs synced to Local PC.")
        else:
            print(f"Server reachable but error: {r.status_code}")
    except Exception as e:
        print(f"Connection Failed. Check if API is running on VM and Port 8000 is open in Azure.")
    
    time.sleep(5)