import os
import json
import time
import hashlib
import logging
from threading import Lock
from typing import Dict, Any
from .base_ledger import BaseLedger

log = logging.getLogger("hawkgrid-ledger-local")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DEFAULT_PATH = os.path.join(BASE_DIR, "ledger", "forensic_audit_ledger.jsonl")
LEDGER_FILE = os.getenv("HG_LOCAL_LEDGER_FILE", DEFAULT_PATH)
os.makedirs(os.path.dirname(LEDGER_FILE), exist_ok=True)
_write_lock = Lock()

def _get_last_hash() -> str:
    """Reads the last line of the file to get the previous block's hash."""
    if not os.path.exists(LEDGER_FILE) or os.stat(LEDGER_FILE).st_size == 0:
        return "0" * 64

    try:
        with open(LEDGER_FILE, "rb") as f:
            f.seek(0, os.SEEK_END)
            position = f.tell()
            
            buffer = b""
            while position > 0:
                position -= 1
                f.seek(position)
                char = f.read(1)
                if char == b"\n" and buffer:
                    break
                buffer = char + buffer
            
            last_line = buffer.decode().strip()
            if last_line:
                return json.loads(last_line).get("hash", "0" * 64)
    except Exception as e:
        log.error(f"Error reading last hash: {e}")
        
    return "0" * 64

def _hash_entry(entry: dict) -> str:
    """Generates a SHA-256 hash of the JSON entry."""
    payload = json.dumps(entry, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()

class LocalLedger(BaseLedger):
    def log_incident(self, incident: Dict[str, Any], response_action: str) -> Dict[str, Any]:
        """Appends a new hashed block to the local forensic ledger."""
        with _write_lock:
            prev_hash = _get_last_hash()

            record = {
                "timestamp": time.time(),
                "incident": incident, 
                "response_action": response_action,
                "previous_hash": prev_hash
            }
            record["hash"] = _hash_entry(record)
            try:
                with open(LEDGER_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record) + "\n")
                    f.flush()
                
                log.info(f"Local forensic block appended to {LEDGER_FILE}")
                return record
            except Exception as e:
                log.exception("Local ledger write failed")
                raise