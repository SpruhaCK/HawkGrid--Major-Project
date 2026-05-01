import logging
import ipaddress
from typing import Dict

log = logging.getLogger("hive_mind")

def is_protected_ip(ip_string: str, router_public_ip: str) -> bool:
    """Checks if the attacker IP is your home router OR a local Kali VM IP."""
    try:
        ip_obj = ipaddress.ip_address(ip_string)
        # Shield activates if it's a private network IP or your router's public IP
        if ip_obj.is_private or ip_string == router_public_ip:
            return True
    except ValueError:
        pass
    return False

def execute_standard_block(incident_data: dict, target_provider_name: str, all_providers: dict, whitelisted_ip: str = None) -> dict:
    attacker_ip = incident_data.get("src_ip", "unknown")
    
    # 🚨 HAWKGRID LOCAL SHIELD
    if is_protected_ip(attacker_ip, whitelisted_ip):
        print(f"    [🛡️ HAWKGRID SHIELD] Standard Block bypassed. Local/Presenter IP {attacker_ip} is protected.")
        return {"status": "SUCCESS", "action": "ALERT_ONLY_WHITELISTED_IP", "details": "Presenter IP protected."}

    target_provider = all_providers.get(target_provider_name)
    if target_provider:
        print(f"[*] Executing Standard Block on {target_provider_name.upper()}...")
        try:
            return target_provider.block_ip(attacker_ip)
        except Exception as e:
            log.error(f"Failed to block IP on {target_provider_name}: {e}")
            return {"status": "FAILED", "action": "ERROR"}
    
    return {"status": "FAILED", "action": "PROVIDER_NOT_FOUND"}

def execute_cross_cloud_quarantine(incident_data: dict, target_provider_name: str, all_providers: dict, whitelisted_ip: str = None) -> dict:
    attacker_ip = incident_data.get("src_ip", "unknown")

    print("\n" + "="*60)
    print(f"🚨 HIVE MIND ACTIVATED: Multi-Cloud Defense Mesh Engaged")
    print(f"🚨 Threat IP: {attacker_ip}")
    print("="*60)
    
    # 🚨 HAWKGRID LOCAL SHIELD
    if is_protected_ip(attacker_ip, whitelisted_ip):
        print(f"    [🛡️ HAWKGRID SHIELD] Global Quarantine bypassed. Local/Presenter IP {attacker_ip} is protected.")
        print("="*60 + "\n")
        return {"status": "SUCCESS", "action": "ALERT_ONLY_WHITELISTED_IP", "details": "Presenter IP protected."}

    results = []
    print(f"[*] Broadcasting Threat IP to Cross-Cloud Firewalls...")
    
    for name, provider in all_providers.items():
        try:
            print(f"    -> Broadcasting block to {name.upper()}...")
            res = provider.block_ip(attacker_ip)
            results.append({"provider": name, "action": res.get("action", "FAILED")})
        except Exception as e:
            print(f"    -> [!] Failed to block on {name.upper()}: {e}")
            results.append({"provider": name, "action": "ERROR"})
            
    print("="*60 + "\n")
    return {"status": "HIVE_MIND_SUCCESS", "action": "CROSS_CLOUD_QUARANTINE", "details": results}