import json
import hashlib
import os

os.makedirs("logs", exist_ok=True)
LOG_FILE = "logs/events.log"

def get_last_hash():
    """
    Reads the last line of the log file to retrieve the previous hash.
    Returns a string of 64 zeros if the file is empty or doesn't exist.
    """
    if not os.path.exists(LOG_FILE) or os.stat(LOG_FILE).st_size == 0:
        return "0" * 64
    
    try:
        with open(LOG_FILE, "rb") as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)
                if f.tell() == 0: break
            
            last_line = f.readline().decode().strip()
            if last_line:
                return json.loads(last_line).get("hash", "0" * 64)
    except Exception:
        return "0" * 64
    
    return "0" * 64

def log_event(ev):
    """
    Logs an event with a cryptographic link to the previous entry.
    """
    prev_hash = get_last_hash()
    
    log_entry = {
        "event": ev,
        "previous_hash": prev_hash
    }
    
    entry_string = json.dumps(log_entry, sort_keys=True)
    current_hash = hashlib.sha256(entry_string.encode()).hexdigest()
    
    final_record = {
        "hash": current_hash,
        "previous_hash": prev_hash,
        "event": ev
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(final_record) + "\n")
    
    return current_hash