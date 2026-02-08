import os
import json
import time
import hashlib

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEDGER_DIR = os.path.join(PROJECT_ROOT, "ledger")
os.makedirs(LEDGER_DIR, exist_ok=True)

LEDGER_FILE = os.path.join(LEDGER_DIR, "forensic_audit_ledger.jsonl")

def get_last_hash() -> str:
    """
    Reads the last line of the ledger file to retrieve the 'hash' of the previous block.
    Returns 64 zeros (Genesis Block) if file is empty or missing.
    """
    if not os.path.exists(LEDGER_FILE) or os.stat(LEDGER_FILE).st_size == 0:
        return "0" * 64
    
    try:
        with open(LEDGER_FILE, "rb") as f:
            try:
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b"\n":
                    f.seek(-2, os.SEEK_CUR)
                    if f.tell() == 0: break
            except OSError:
                f.seek(0)
            
            last_line = f.readline().decode().strip()
            if last_line:
                last_entry = json.loads(last_line)
                return last_entry.get("hash", "0" * 64)
                
    except Exception as e:
        print(f"[!] Ledger Read Error: {e}")
        return "0" * 64

    return "0" * 64


def _hash_entry(entry: dict) -> str:
    """Generates SHA-256 hash of the dictionary entry."""
    # We sort keys to ensure the hash is deterministic
    payload = json.dumps(entry, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def log_incident_to_ledger(incident: dict, response_action: str):
    """
    Logs a high-value incident with a cryptographic link to the previous entry.
    """
    # 1. Get the Link (Will be 0000... if previous log was old format)
    prev_hash = get_last_hash()

    # 2. Create the Block
    record = {
        "timestamp": time.time(),
        "incident": incident,
        "response_action": response_action,
        "previous_hash": prev_hash  
    }

    # 3. Seal the Block (Hash the whole thing, including the previous link)
    record["hash"] = _hash_entry(record)

    # 4. Write to Append-Only Ledger
    try:
        with open(LEDGER_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return record
    except Exception as e:
        print(f"[!] Ledger Write Error: {e}")
        return None