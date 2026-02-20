import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_FILE = os.path.join(BASE_DIR, "../../reports/forensic_audit.json")

def build_report(raw_event, detection, response_action):
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "raw_event": raw_event,
        "detection": detection,
        "response": response_action
    }

def append_report(report: dict):
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    
    data = []
    if os.path.exists(REPORT_FILE) and os.path.getsize(REPORT_FILE) > 0:
        try:
            with open(REPORT_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

    data.append(report)
    with open(REPORT_FILE, "w") as f:
        json.dump(data, f, indent=4)