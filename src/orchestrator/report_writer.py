"""
Forensic report writer
Safe for Windows / Linux / Docker
"""

import os
import json
import time

BASE_DIR = os.getenv(
    "HG_REPORT_DIR",
    os.path.join(os.getcwd(), "reports")
)

os.makedirs(BASE_DIR, exist_ok=True)

REPORT_FILE = os.path.join(BASE_DIR, "forensic_audit.json")


def build_report(raw_event, detection, response_action):
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "raw_event": raw_event,
        "detection": detection,
        "response": response_action
    }


def append_report(report: dict):
    try:
        if os.path.exists(REPORT_FILE):
            with open(REPORT_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []

        data.append(report)

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        print(f"[REPORT ERROR] {e}")
