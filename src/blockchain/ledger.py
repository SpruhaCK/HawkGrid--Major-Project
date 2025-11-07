import hashlib
import json
import time
import os
import logging
# --- CRITICAL: Use the absolute path for import ---
from src.blockchain.es_logger import log_to_elasticsearch 

# --- Configuration ---
# File where the hash chain is physically stored locally (simulating the ledger)
LEDGER_FILE = '/app/forensic_audit_ledger.jsonl' 

# Set up logging for module debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_last_hash() -> str:
    """Reads the current_hash of the last recorded incident to establish the chain of custody."""
    if not os.path.exists(LEDGER_FILE):
        return "0" * 64 
    
    try:
        with open(LEDGER_FILE, 'r') as f:
            lines = f.readlines()
            # Find the last non-empty line
            for line in reversed(lines):
                stripped_line = line.strip()
                if stripped_line:
                    last_entry = json.loads(stripped_line)
                    # Safely retrieve the current_hash
                    return last_entry.get('current_hash', '0' * 64)
    except Exception:
        # If the file is corrupted or unreadable, we reset the chain but log the failure
        logging.error("Ledger file corruption detected. Restarting hash chain.")
        return "0" * 64
    return "0" * 64

def log_incident_to_ledger(incident_data: dict, response_action: str) -> dict:
    """
    1. Creates immutable entry by linking to the previous hash.
    2. Writes the hash chain entry to a local file.
    3. Sends the report to Elasticsearch.
    """
    
    # 1. Prepare the Data Block (Capturing all required info)
    incident_details = {
        "incident_time": incident_data.get("timestamp", time.time()),
        "node_id": incident_data.get("node_id"),
        "cloud_provider": incident_data.get("cloud_provider"),
        "anomaly_score": incident_data.get("anomaly_score"),
        
        # --- MERGED FIELD: Attack Type ---
        "attack_type": incident_data.get("attack_type_classified", "UNCATEGORIZED_ANOMALY"), 
        
        "response_action": response_action,
        "previous_hash": get_last_hash(), # Link to the previous block's hash
        "log_sequence_id": int(time.time() * 1000) 
    }
    
    # 2. Calculate the Hash (The immutable proof of evidence)
    # Ensure consistent formatting (sort_keys=True) for reliable hashing
    data_string = json.dumps(incident_details, sort_keys=True)
    current_hash = hashlib.sha256(data_string.encode('utf-8')).hexdigest()
    incident_details["current_hash"] = current_hash
    
    # 3. Write to Local Ledger File (The audit trail)
    try:
        with open(LEDGER_FILE, 'a') as f:
            f.write(json.dumps(incident_details) + '\n')
    except Exception as e:
        logging.error(f"Failed to write to local ledger file: {e}")
    
    # 4. Send to Elasticsearch (For Kibana Visualization)
    log_to_elasticsearch(incident_details)
        
    return incident_details
# ```

# ---

# ## 💻 Phase 2: Integrated Orchestrator (`src/orchestrator/api.py`)

# This file contains the final, integrated logic for detection and classification. You provided the correct code for this file in our last exchange, but please verify it is up-to-date in your system.

# ### 2. Final Action: Test the Integrated System

# 1.  **Stop and Clean:**
#     ```bash
#     docker-compose down -v
#     ```
# 2.  **Rebuild and Start:**
#     ```bash
#     docker-compose up --build -d
#     ```

# Wait 10 seconds, and then run the test to check the entire chain, confirming the **Attack Type** is now included in the output report:

# ```bash
# curl -X POST http://localhost:8000/api/detect -H "Content-Type: application/json" -d '{"Network_Egress_MB": 400.0, "API_Call_Freq": 250.0, "Failed_Auth_Count": 5.0, "node_id": "Azure-VM-A"}'
