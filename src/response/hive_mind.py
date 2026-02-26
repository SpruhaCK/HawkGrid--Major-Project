# import logging
# from typing import Dict

# log = logging.getLogger("hive_mind")

# def execute_cross_cloud_quarantine(incident_data: Dict, target_provider_name: str, all_providers: Dict) -> Dict:
#     attacker_ip = incident_data.get("src_ip", "unknown")
#     target_node = incident_data.get("node_id", "unknown")
    
#     print("\n" + "="*60)
#     print(f"🚨 HIVE MIND ACTIVATED: Multi-Cloud Defense Mesh Engaged")
#     print(f"🚨 Threat IP: {attacker_ip}")
#     print("="*60)

#     results = []

#     # Phase 1: Isolate specific cloud
#     target_provider = all_providers.get(target_provider_name)
#     if target_provider:
#         print(f"[*] Phase 1: Isolating compromised node '{target_node}' on {target_provider_name.upper()}...")
#         target_provider.isolate_instance(incident_data)
#         results.append({"provider": target_provider_name, "action": "INSTANCE_ISOLATED"})
#     else:
#         log.error(f"Target provider {target_provider_name} not found in active providers.")

#     # Phase 2: Block IP on ALL clouds
#     print(f"[*] Phase 2: Broadcasting Threat IP to Cross-Cloud Firewalls...")
#     for name, provider in all_providers.items():
#         try:
#             provider.block_ip(attacker_ip)
#             results.append({"provider": name, "action": "IP_BLOCKED"})
#         except Exception as e:
#             log.error(f"Failed to block IP on {name}: {e}")

#     print("="*60 + "\n")

#     return {
#         "status": "HIVE_MIND_SUCCESS",
#         "action": "CROSS_CLOUD_QUARANTINE",
#         "details": results
#     }

# def execute_standard_block(incident_data: Dict, target_provider_name: str, all_providers: Dict) -> Dict:
#     attacker_ip = incident_data.get("src_ip", "unknown")
#     target_provider = all_providers.get(target_provider_name)
    
#     if target_provider:
#         print(f"\n[*] Standard Playbook: Blocking {attacker_ip} only on {target_provider_name.upper()}.")
#         target_provider.block_ip(attacker_ip)
#         return {"status": "SUCCESS", "action": "SINGLE_CLOUD_BLOCK", "provider": target_provider_name}
    
#     return {"status": "FAILED", "action": "PROVIDER_NOT_FOUND"}

import logging
from typing import Dict

log = logging.getLogger("hive_mind")

def execute_cross_cloud_quarantine(incident_data: Dict, target_provider_name: str, all_providers: Dict, whitelisted_ip: str) -> Dict:
    attacker_ip = incident_data.get("src_ip", "unknown")

    print("\n" + "="*60)
    print(f"🚨 HIVE MIND ACTIVATED: Multi-Cloud Defense Mesh Engaged")
    print(f"🚨 Threat IP: {attacker_ip}")
    print("="*60)

    # 🚨 DYNAMIC PRESENTER PROTECTION
    if attacker_ip == whitelisted_ip:
        print(f"[*] THREAT DETECTED & LOGGED. Blocking bypassed for Presenter Network ({attacker_ip}).")
        print("="*60 + "\n")
        return {"status": "LOGGED_ONLY", "action": "WHITELIST_BYPASS"}

    results = []
    print(f"[*] Broadcasting Threat IP to Cross-Cloud Firewalls...")
    
    for name, provider in all_providers.items():
        try:
            provider.block_ip(attacker_ip)
            results.append({"provider": name, "action": "IP_BLOCKED"})
        except Exception as e:
            log.error(f"Failed to block IP on {name}: {e}")

    print("="*60 + "\n")
    return {"status": "HIVE_MIND_SUCCESS", "action": "CROSS_CLOUD_QUARANTINE", "details": results}

def execute_standard_block(incident_data: Dict, target_provider_name: str, all_providers: Dict) -> Dict:
    attacker_ip = incident_data.get("src_ip", "unknown")
    print(f"\n[*] Standard Playbook: Blocking {attacker_ip} only on {target_provider_name.upper()}.")
    
    target_provider = all_providers.get(target_provider_name)
    if target_provider:
        target_provider.block_ip(attacker_ip)
        return {"status": "SUCCESS", "action": "SINGLE_CLOUD_BLOCK"}
    
    return {"status": "FAILED", "action": "PROVIDER_NOT_FOUND"}