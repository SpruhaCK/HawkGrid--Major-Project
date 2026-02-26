# import os
# import logging
# from typing import Dict, List
# from azure.identity import DefaultAzureCredential
# from azure.mgmt.compute import ComputeManagementClient
# from src.cloud.base_provider import CloudProvider

# log = logging.getLogger("azure_provider")

# class AzureProvider(CloudProvider):
#     def __init__(self):
#         self.name = "azure"
#         self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        
#         if not self.subscription_id:
#             raise EnvironmentError("AZURE_SUBSCRIPTION_ID not set")
            
#         try:
#             credential = DefaultAzureCredential()
#             self.client = ComputeManagementClient(credential, self.subscription_id)
#             self.mock_mode = False
#             log.info("Azure SDK authenticated successfully.")
#         except Exception as e:
#             log.warning(f"Failed to authenticate with Azure SDK. Running in MOCK mode.")
#             self.mock_mode = True

#     def discover_assets(self) -> List[Dict]:
#         assets = []
#         if not self.mock_mode:
#             try:
#                 for vm in self.client.virtual_machines.list_all():
#                     assets.append({
#                         "node_id": vm.name,
#                         "public_ip": None,
#                         "private_ip": None,
#                         "status": "running"
#                     })
#             except Exception as e:
#                 log.error(f"Error discovering Azure assets: {e}")
#         else:
#             assets.append({
#                 "node_id": "azure-vm-east-1",
#                 "public_ip": "20.119.0.55", 
#                 "private_ip": "10.2.0.4",
#                 "status": "running"
#             })
#         return assets

#     def resolve_private_ip(self, public_ip: str) -> str:
#         return public_ip

#     def block_ip(self, attacker_ip: str) -> dict:
#         print(f"    [AZURE-NSG] 🛡️ Action: Updating Azure NSG Rules...")
#         print(f"    [AZURE-NSG] 🚫 DENY INBOUND: {attacker_ip} globally.")
#         return {"status": "SUCCESS", "action": "NSG_IP_BLOCKED", "provider": "azure"}

#     def isolate_instance(self, incident: Dict) -> bool:
#         node_id = incident.get('node_id', 'unknown')
#         print(f"    [AZURE] ⚠️ ISOLATING VM: {node_id}")
#         return True

import os
import logging
from typing import Dict
from src.cloud.base_provider import CloudProvider

log = logging.getLogger("hawkgrid-provider")

def _aws_ready():
    return (
        bool(os.getenv("AWS_REGION")) and
        bool(os.getenv("AWS_ACCESS_KEY_ID")) and
        bool(os.getenv("AWS_SECRET_ACCESS_KEY"))
    )

def _azure_ready():
    # 🚨 FORCED TRUE FOR NOW: Ensures Mock Azure loads for the Hive Mind test
    return True

def get_cloud_providers() -> Dict[str, CloudProvider]:
    providers = {}

    if _aws_ready():
        try:
            from src.cloud.aws_provider import AWSProvider
            aws = AWSProvider()
            aws.discover_assets()
            providers[aws.name] = aws
            log.info("AWS provider READY")
        except Exception as e:
            log.warning(f"AWS provider skipped: {e}")
    else:
        log.info("AWS env not configured")

    if _azure_ready():
        try:
            from src.cloud.azure_provider import AzureProvider
            az = AzureProvider()
            az.discover_assets()
            providers[az.name] = az
            log.info("Azure provider READY (MOCK MODE)")
        except Exception as e:
            log.warning(f"Azure provider skipped: {e}")
    else:
        log.info("Azure env not configured")

    if not providers:
        log.warning("No cloud providers READY. Running standalone mode.")
    else:
        log.info(f"Active providers: {list(providers.keys())}")
        
    return providers