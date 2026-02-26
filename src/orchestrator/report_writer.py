import os
import json
import time
import hashlib
from datetime import datetime, timezone, timedelta

BASE_DIR = os.getenv(
    "HG_REPORT_DIR",
    os.path.join(os.getcwd(), "reports")
)

os.makedirs(BASE_DIR, exist_ok=True)
REPORT_FILE = os.path.join(BASE_DIR, "forensic_audit.json")

def calculate_hash(data_block: dict) -> str:
    """Generates a SHA-256 hash for the block string."""
    # We use sort_keys to ensure the hash is consistent regardless of key order
    block_string = json.dumps(data_block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def get_last_hash():
    """Reads the last line of the file to find the previous current_hash."""
    if not os.path.exists(REPORT_FILE) or os.path.getsize(REPORT_FILE) == 0:
        return "0"
    
    try:
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last_line = json.loads(lines[-1].strip())
                return last_line.get("current_hash", "0")
    except Exception:
        return "0"
    return "0"

def build_report(raw_event, detection, response_action):
    """
    Extracts real data from raw_event and maps it to a flat structure.
    This fixes the 'string' placeholder issue from Swagger.
    """
    # Use .get() to find real values, defaulting to 'N/A' if not provided
    src_ip = raw_event.get("src_ip", "N/A")
    dst_ip = raw_event.get("dst_ip", "N/A")
    
    prev_h = get_last_hash()

    # The block structure
    report = {
        # Change your timestamp line to this:
        "timestamp": datetime.now().isoformat(),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "detection": detection,
        "response": response_action,
        "previous_hash": prev_h
    }
    
    # Calculate the hash for this specific block
    report["current_hash"] = calculate_hash(report)
    return report

def append_report(report_data: dict):
    """Appends the report as a single line (JSONL) to the ledger."""
    try:
        # 1. Build the dictionary with real data and hashes
        final_block = build_report(
            report_data.get("raw_event", {}),
            report_data.get("detection", "Unknown"),
            report_data.get("response", "None")
        )

        # 2. Convert to a single-line string (no indent) and append
        with open(REPORT_FILE, "a", encoding="utf-8") as f:
            line = json.dumps(final_block)
            f.write(line + "\n")
            
        return final_block["current_hash"]

    except Exception as e:
        print(f"[REPORT ERROR] {e}")
        return None