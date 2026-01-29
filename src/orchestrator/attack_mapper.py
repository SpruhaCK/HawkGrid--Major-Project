# src/orchestrator/attack_mapper.py

from datetime import datetime

def map_attack_type(event: dict) -> str:
    """
    SOC-Grade Classification Logic.
    Translates raw telemetry into specific attack names.
    """
    api_freq = event.get("API_Call_Freq", 0)
    failed_auth = event.get("Failed_Auth_Count", 0)
    egress = event.get("Network_Egress_MB", 0)

    if api_freq >= 500:
        return "DDoS_ATTACK"

    if api_freq >= 200 or egress >= 500:
        return "DoS_ATTACK"

    # 3. Brute Force: Check for failed logins (Demo sends 60)
    if failed_auth >= 40:
        return "BRUTE_FORCE"

    # 4. DoS/Port Scan: Check moderate-high frequency
    if api_freq >= 80:
        return "PORT_SCAN"

    # 5. Low-level suspicious activity
    if fail_auth >= 3 or api_freq > 15:
        return "GENERIC_ANOMALY"

    return "NORMAL"

# def map_attack_type(event: dict) -> str:
#     """
#     Rule-based attack classification (SOC-grade)
#     """

#     if event["Failed_Auth_Count"] > 40:
#         return "BRUTE_FORCE"

#     if event["API_Call_Freq"] > 60 and event["Network_Egress_MB"] > 80:
#         return "PORT_SCAN"

#     if event["Network_Egress_MB"] > 500:
#         return "DATA_EXFILTRATION"

#     if event["API_Call_Freq"] > 100:
#         return "DDoS"

#     return "UNKNOWN_ANOMALY"

def map_attack_to_features(
    attack_type: str,
    src_ip: str = "unknown",
    dst_ip: str = "ec2-victim"
):
    """
    Converts a known attack pattern into UNSW-like numeric features.
    Used ONLY for controlled demo + evaluation.
    """

    base = {
        "node_id": dst_ip,
        "cloud_provider": "aws",
        "timestamp": datetime.utcnow().isoformat(),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
    }

    if attack_type == "PORT_SCAN":
        base.update({
            "API_Call_Freq": 80,
            "Failed_Auth_Count": 0,
            "Network_Egress_MB": 15.0
        })

    elif attack_type == "BRUTE_FORCE":
        base.update({
            "API_Call_Freq": 10,
            "Failed_Auth_Count": 60,
            "Network_Egress_MB": 5.0
        })

    elif attack_type == "DOS":
        base.update({
            "API_Call_Freq": 250,
            "Failed_Auth_Count": 0,
            "Network_Egress_MB": 600.0
        })

    elif attack_type == "DDoS":
        base.update({
            "API_Call_Freq": 550,
            "Failed_Auth_Count": 0,
            "Network_Egress_MB": 10.0
        })

    else:
        base.update({
            "API_Call_Freq": 2,
            "Failed_Auth_Count": 0,
            "Network_Egress_MB": 1.0
        })

    return base
