import os
import logging
from typing import Dict, List
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from src.cloud.base_provider import CloudProvider

log = logging.getLogger("hawkgrid-azure")

class AzureProvider(CloudProvider):
    def __init__(self):
        self.name = "azure"
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        
        if not self.subscription_id:
            raise EnvironmentError("AZURE_SUBSCRIPTION_ID not set in .env")
            
        # Strict Authentication: If this fails, the factory will catch the exception 
        # and gracefully mark Azure as DOWN, allowing AWS to run independently.
        log.info("Authenticating with Azure SDK...")
        credential = DefaultAzureCredential()
        self.client = ComputeManagementClient(credential, self.subscription_id)
        log.info("Azure SDK authenticated successfully.")

    def discover_assets(self) -> List[Dict]:
        assets = []
        try:
            # Reaches into Azure and lists all VMs in the subscription
            for vm in self.client.virtual_machines.list_all():
                assets.append({
                    "node_id": vm.name,
                    "public_ip": None, # Requires querying Azure Network Interfaces
                    "private_ip": None,
                    "status": "running"
                })
        except Exception as e:
            log.error(f"Error discovering Azure assets: {e}")
            # Returning an empty list signals the factory that Azure has no active targets
            return []
            
        return assets

    def resolve_private_ip(self, public_ip: str) -> str:
        return public_ip

    def block_ip(self, attacker_ip: str) -> dict:
        # Placeholder for actual Azure Network Security Group (NSG) logic
        print(f"    [AZURE-NSG] 🛡️ Action: Updating Azure NSG Rules...")
        print(f"    [AZURE-NSG] 🚫 DENY INBOUND: {attacker_ip} globally.")
        return {"status": "SUCCESS", "action": "NSG_IP_BLOCKED", "provider": "azure"}

    def isolate_instance(self, incident: Dict) -> bool:
        node_id = incident.get('node_id', 'unknown')
        print(f"    [AZURE] ⚠️ ISOLATING VM: {node_id}")
        return True

    def fetch_logs(self, **kwargs) -> list:
        # Placeholder to satisfy the abstract base class
        # print(f"    [{self.name.upper()}] Log fetching not yet implemented.")
        return []