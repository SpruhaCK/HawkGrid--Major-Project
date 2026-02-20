import os
import boto3
from typing import Dict, List
from src.cloud.base_provider import CloudProvider


class AWSProvider(CloudProvider):

    def __init__(self):
        self.region = os.getenv("AWS_REGION")
        if not self.region:
            raise EnvironmentError("AWS_REGION not set")

        self.client = boto3.client("ec2", region_name=self.region)

    def discover_assets(self) -> List[Dict]:
        response = self.client.describe_instances(
            Filters=[
                {"Name": "instance-state-name", "Values": ["running"]}
            ]
        )

        assets = []

        for r in response["Reservations"]:
            for i in r["Instances"]:
                assets.append({
                    "public_ip": i.get("PublicIpAddress"),
                    "private_ip": i.get("PrivateIpAddress")
                })

        return assets

    def resolve_private_ip(self, public_ip: str) -> str:
        response = self.client.describe_instances(
            Filters=[{"Name": "ip-address", "Values": [public_ip]}]
        )

        for r in response["Reservations"]:
            for i in r["Instances"]:
                return i.get("PrivateIpAddress")

        return public_ip

    def isolate_instance(self, incident: Dict) -> bool:
        # Example containment logic
        print(f"[AWS] Isolating instance {incident.get('node_id')}")
        return True