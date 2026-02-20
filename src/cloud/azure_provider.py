import os
from typing import Dict, List
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from src.cloud.base_provider import CloudProvider


class AzureProvider(CloudProvider):

    def __init__(self):
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        if not subscription_id:
            raise EnvironmentError("AZURE_SUBSCRIPTION_ID not set")

        credential = DefaultAzureCredential()
        self.client = ComputeManagementClient(credential, subscription_id)

    def discover_assets(self) -> List[Dict]:
        assets = []

        for vm in self.client.virtual_machines.list_all():
            assets.append({
                "public_ip": None,   # must fetch NIC for real IP
                "private_ip": None
            })

        return assets

    def resolve_private_ip(self, public_ip: str) -> str:
        # Azure requires NIC lookup — simplified
        return public_ip

    def isolate_instance(self, incident: Dict) -> bool:
        print(f"[AZURE] Isolating VM {incident.get('node_id')}")
        return True