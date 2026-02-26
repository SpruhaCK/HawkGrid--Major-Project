from datetime import datetime, timezone

def map_attack_type(event: dict) -> str:
    """
    SOC-Grade Classification Logic.
    Refined for 2-second window aggregation and real-time sensor data.
    """
    # Extract features with defaults to prevent crashes
    api_freq = event.get("API_Call_Freq", 0)
    failed_auth = event.get("Failed_Auth_Count", 0)
    egress = event.get("Network_Egress_MB", 0)

    # 1. DDoS: Extremely high volume
    if api_freq >= 500: 
        return "DDoS_ATTACK"

    # 2. DoS: High volume or heavy bandwidth exhaustion
    if api_freq >= 200 or egress >= 500: 
        return "DoS_ATTACK"

    # 3. Port Scan: 
    # Adjusted threshold to > 25 to catch your Nmap frequency (30.0 - 60.0)
    # Scans typically have low data egress.
    if api_freq >= 25 and egress < 10.0:
        return "PORT_SCAN"

    # 4. Brute Force: Targeted at authentication attempts
    if failed_auth >= 10: 
        return "BRUTE_FORCE"

    # 5. Generic Anomaly: Catch-all for suspicious activity
    if failed_auth >= 3 or api_freq > 15:
        return "GENERIC_ANOMALY"

    return "NORMAL"

def map_attack_to_features(attack_type: str, src_ip: str = "unknown", dst_ip: str = "ec2-victim"):
    """
    Simulates attack 'shapes' for controlled demos and unit testing.
    """
    base = {
        "node_id": dst_ip,
        "cloud_provider": "azure",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
    }

    # Simulation Logic for testing
    logic = {
        "PORT_SCAN":   {"API_Call_Freq": 80,  "Failed_Auth_Count": 0,  "Network_Egress_MB": 2.0},
        "BRUTE_FORCE": {"API_Call_Freq": 15,  "Failed_Auth_Count": 60, "Network_Egress_MB": 1.0},
        "DOS":         {"API_Call_Freq": 300, "Failed_Auth_Count": 0,  "Network_Egress_MB": 700.0},
        "DDOS":        {"API_Call_Freq": 600, "Failed_Auth_Count": 0,  "Network_Egress_MB": 5.0},
    }

    features = logic.get(attack_type.upper(), {"API_Call_Freq": 2, "Failed_Auth_Count": 0, "Network_Egress_MB": 0.5})
    base.update(features)
    
    # Add ML-specific required fields for compatibility
    base.update({"rate": 1.0, "sttl": 64.0, "sbytes": 1024.0})
    
    return base