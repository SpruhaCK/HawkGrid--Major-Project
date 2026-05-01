import os
import json
import hashlib
from datetime import datetime, timezone

BASE_DIR = os.getenv("HG_REPORT_DIR", os.path.join(os.getcwd(), "reports"))
os.makedirs(BASE_DIR, exist_ok=True)
REPORT_FILE = os.path.join(BASE_DIR, "forensic_audit.json")

def calculate_hash(data_block: dict) -> str:
    block_string = json.dumps(data_block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def get_last_hash():
    # If file doesn't exist or is empty, return genesis hash
    if not os.path.exists(REPORT_FILE) or os.path.getsize(REPORT_FILE) == 0:
        return "0" * 64
    
    try:
        # Read the file as a complete JSON list
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # If it's a list and has items, get the hash from the last item
            if isinstance(data, list) and len(data) > 0:
                last_item = data[-1]
                return last_item.get("current_hash", "0" * 64)
    except Exception:
        # If the JSON is completely broken, fall back to genesis
        return "0" * 64
        
    return "0" * 64

def build_report(raw_event, detection, response_action):
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "src_ip": raw_event.get("src_ip", "N/A"),
        "dst_ip": raw_event.get("dst_ip", "N/A"),
        "raw_event": raw_event,
        "detection": detection,
        "response": response_action,
        "previous_hash": get_last_hash()
    }
    report["current_hash"] = calculate_hash(report)
    return report

def append_report(report_data: dict):
    try:
        existing_data = []
        
        # 1. Read the existing array (if the file exists and isn't empty)
        if os.path.exists(REPORT_FILE) and os.path.getsize(REPORT_FILE) > 0:
            with open(REPORT_FILE, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                    # Safety check: if somehow it's not a list, wrap it
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                except json.JSONDecodeError:
                    # If the file was corrupted by the old code, wipe it and start fresh
                    print("[REPORT WARNING] Existing forensic_audit.json is corrupted. Starting fresh array.")
                    existing_data = []

        # 2. Append the new report dictionary to the list
        existing_data.append(report_data)

        # 3. Write the entire list back to the file as a pretty-printed JSON array
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4)
            
        return report_data.get("current_hash")
    except Exception as e:
        print(f"[REPORT ERROR] {e}")
        return None