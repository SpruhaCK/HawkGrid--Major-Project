from datetime import datetime

def map_attack_type(event: dict) -> str:
    """
    SOC-Grade Classification Logic.
    Refined for 2-second window aggregation.
    """
    api_freq = event.get("API_Call_Freq", 0)
    failed_auth = event.get("Failed_Auth_Count", 0)
    egress = event.get("Network_Egress_MB", 0)

    # 1. DDoS: Extremely high volume, often small packets
    if api_freq >= 500: 
        return "DDoS_ATTACK"

    # 2. DoS: High volume with significant data transfer (exhausting bandwidth)
    if api_freq >= 200 or egress >= 500: 
        return "DoS_ATTACK"

    # 3. Port Scan: High frequency but very low data per packet
    # A scan hits many ports but sends almost no actual data
    if api_freq >= 50 and egress < 5.0 and failed_auth < 2:
        return "PORT_SCAN"

    # 4. Brute Force: Targeted at auth ports (22, 3389)
    if failed_auth >= 10: 
        return "BRUTE_FORCE"

    # 5. Generic Anomaly: Catch-all for suspicious but low-volume activity
    if failed_auth >= 3 or api_freq > 20:
        return "GENERIC_ANOMALY"

    return "NORMAL"

def map_attack_to_features(attack_type: str, src_ip: str = "unknown", dst_ip: str = "ec2-victim"):
    """
    Used for controlled demos/unit testing to simulate attack 'shapes'.
    """
    base = {
        "node_id": dst_ip,
        "cloud_provider": "aws",
        "timestamp": datetime.utcnow().isoformat(),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
    }

    # Map attack types to simulated UNSW-NB15 features
    # Format: {API_Call_Freq (rate), Failed_Auth_Count (sttl), Network_Egress_MB (sbytes)}
    logic = {
        "PORT_SCAN":   {"API_Call_Freq": 80,  "Failed_Auth_Count": 0,  "Network_Egress_MB": 2.0},
        "BRUTE_FORCE": {"API_Call_Freq": 15,  "Failed_Auth_Count": 60, "Network_Egress_MB": 1.0},
        "DOS":         {"API_Call_Freq": 300, "Failed_Auth_Count": 0,  "Network_Egress_MB": 700.0},
        "DDoS":        {"API_Call_Freq": 600, "Failed_Auth_Count": 0,  "Network_Egress_MB": 5.0},
    }

    base.update(logic.get(attack_type.upper(), {"API_Call_Freq": 2, "Failed_Auth_Count": 0, "Network_Egress_MB": 0.5}))
    return base