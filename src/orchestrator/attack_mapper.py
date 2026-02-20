import os
from datetime import datetime


def map_attack_type(event: dict) -> str:
    api_freq = event.get("API_Call_Freq", 0)
    failed_auth = event.get("Failed_Auth_Count", 0)
    egress = event.get("Network_Egress_MB", 0)

    if api_freq >= 500:
        return "DDoS_ATTACK"

    if api_freq >= 200 or egress >= 500:
        return "DoS_ATTACK"

    if api_freq >= 50 and egress < 5.0 and failed_auth < 2:
        return "PORT_SCAN"

    if failed_auth >= 10:
        return "BRUTE_FORCE"

    if failed_auth >= 3 or api_freq > 20:
        return "GENERIC_ANOMALY"

    return "NORMAL"


def map_attack_to_features(attack_type: str, src_ip: str = "unknown", dst_ip: str = "unknown"):

    base = {
        "node_id": dst_ip,
        "cloud_provider": os.getenv("HG_CLOUD_PROVIDER", "unknown"),
        "timestamp": datetime.utcnow().isoformat(),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
    }

    logic = {
        "PORT_SCAN":   {"API_Call_Freq": 80,  "Failed_Auth_Count": 0,  "Network_Egress_MB": 2.0},
        "BRUTE_FORCE": {"API_Call_Freq": 15,  "Failed_Auth_Count": 60, "Network_Egress_MB": 1.0},
        "DOS":         {"API_Call_Freq": 300, "Failed_Auth_Count": 0,  "Network_Egress_MB": 700.0},
        "DDOS":        {"API_Call_Freq": 600, "Failed_Auth_Count": 0,  "Network_Egress_MB": 5.0},
    }

    base.update(
        logic.get(
            attack_type.upper(),
            {"API_Call_Freq": 2, "Failed_Auth_Count": 0, "Network_Egress_MB": 0.5}
        )
    )

    return base