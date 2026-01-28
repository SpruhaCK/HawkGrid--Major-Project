# """
# ledger.py

# Implements the LOCAL file-based forensic ledger.
# This is used when USE_LOCAL_LEDGER=true.

# It simulates a blockchain by creating a hash chain in a local .jsonl file.
# It has NO external dependencies (like Elasticsearch) and is self-contained.
# """
# import hashlib
# import json
# import time
# import os
# import logging

# # --- Configuration ---
# # We use /app because the docker-compose.yml maps the project root to /app
# LEDGER_FILE = '/app/forensic_audit_ledger.jsonl' 

# log = logging.getLogger("hawkgrid-ledger-local")
# log.setLevel(logging.INFO)

# def get_last_hash() -> str:
#     """Reads the current_hash of the last recorded incident to establish the chain."""
#     if not os.path.exists(LEDGER_FILE):
#         return "0" * 64 
    
#     try:
#         with open(LEDGER_FILE, 'r') as f:
#             lines = f.readlines()
#             # Find the last non-empty line
#             for line in reversed(lines):
#                 stripped_line = line.strip()
#                 if stripped_line:
#                     last_entry = json.loads(stripped_line)
#                     return last_entry.get('current_hash', '0' * 64)
#     except Exception as e:
#         log.error(f"Ledger file {LEDGER_FILE} corruption detected or unreadable: {e}")
#         return "0" * 64
#     return "0" * 64

# def log_incident_to_ledger(incident_data: dict, response_action: str) -> dict:
#     """
#     1. Creates immutable entry by linking to the previous hash.
#     2. Writes the hash chain entry to the local .jsonl file.
#     3. Returns the new entry.
#     """
    
#     # 1. Prepare the Data Block
#     incident_details = {
#         "incident_time": incident_data.get("timestamp", time.time()),
#         "node_id": incident_data.get("node_id"),
#         "cloud_provider": incident_data.get("cloud_provider"),
#         "anomaly_score": incident_data.get("anomaly_score"),
#         "attack_type": incident_data.get("attack_type", "UNCATEGORIZED_ANOMALY"), 
#         "response_action": response_action,
#         "previous_hash": get_last_hash(), # Link to the previous block's hash
#         "log_sequence_id": int(time.time() * 1000) 
#     }
    
#     # 2. Calculate the Hash
#     data_string = json.dumps(incident_details, sort_keys=True)
#     current_hash = hashlib.sha256(data_string.encode('utf-8')).hexdigest()
#     incident_details["current_hash"] = current_hash
    
#     # 3. Write to Local Ledger File
#     try:
#         with open(LEDGER_FILE, 'a') as f:
#             f.write(json.dumps(incident_details) + '\n')
#         # Use log.critical for high-importance, non-error logs
#         log.critical(f"Local ledger entry created: {current_hash[:12]}...")
#     except Exception as e:
#         log.exception(f"Failed to write to local ledger file: {e}")
#         # Re-raise to be caught by api.py
#         raise
    
#     # 4. Return the full record
#     return incident_details


"""
Local immutable forensic ledger (JSONL)
Safe for demo, Windows, Linux, Docker
"""

import os
import json
import time
import hashlib

# ---- LEDGER PATH (FIXED) ----
BASE_DIR = os.getenv(
    "HG_LEDGER_DIR",
    os.path.join(os.getcwd(), "ledger")
)

os.makedirs(BASE_DIR, exist_ok=True)

LEDGER_FILE = os.path.join(BASE_DIR, "forensic_audit_ledger.jsonl")


def _hash_entry(entry: dict) -> str:
    payload = json.dumps(entry, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def log_incident_to_ledger(incident: dict, response_action: str):
    record = {
        "timestamp": time.time(),
        "incident": incident,
        "response_action": response_action
    }

    record["hash"] = _hash_entry(record)

    with open(LEDGER_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return record
