from datetime import datetime
from src.orchestrator.api import run_detection

def ingest_event(attack_type: str, src_ip="kali", dst="ec2-victim"):
    payload = {
        "node_id": "ec2-victim",
        "cloud_provider": "aws",
        "timestamp": datetime.utcnow().isoformat(),
        "src_ip": src_ip,
        "dst_ip": dst,
        "attack": attack_type
    }
    return run_detection(payload)
