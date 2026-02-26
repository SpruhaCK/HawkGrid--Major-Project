# import os
# import boto3
# from typing import Dict, List
# from src.cloud.base_provider import CloudProvider

# class AWSProvider(CloudProvider):
#     def __init__(self):
#         self.name = "aws"
#         self.region = os.getenv("AWS_REGION")
#         if not self.region:
#             raise EnvironmentError("AWS_REGION not set")
#         self.client = boto3.client("ec2", region_name=self.region)

#     def discover_assets(self) -> List[Dict]:
#         response = self.client.describe_instances(
#             Filters=[
#                 {"Name": "instance-state-name", "Values": ["running"]}
#             ]
#         )
#         assets = []
#         for r in response["Reservations"]:
#             for i in r["Instances"]:
#                 assets.append({
#                     "public_ip": i.get("PublicIpAddress"),
#                     "private_ip": i.get("PrivateIpAddress")
#                 })

#         return assets

#     def resolve_private_ip(self, public_ip: str) -> str:
#         response = self.client.describe_instances(
#             Filters=[{"Name": "ip-address", "Values": [public_ip]}]
#         )
#         for r in response["Reservations"]:
#             for i in r["Instances"]:
#                 return i.get("PrivateIpAddress")

#         return public_ip

#     def block_ip(self, attacker_ip: str) -> dict:
#         print(f"    [AWS-WAF] 🛡️ Action: Updating AWS Network ACLs...")
#         print(f"    [AWS-WAF] 🚫 DENY INBOUND: {attacker_ip} globally.")
#         return {"status": "SUCCESS", "action": "WAF_IP_BLOCKED", "provider": "aws"}

#     def isolate_instance(self, incident: Dict) -> bool:
#         print(f"[AWS] Isolating instance {incident.get('node_id')}")
#         return True

import os
import boto3
from typing import Dict, List
from src.cloud.base_provider import CloudProvider

class AWSProvider(CloudProvider):
    def __init__(self):
        self.name = "aws"
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

    def block_ip(self, attacker_ip: str) -> dict:
        print(f"    [AWS-NACL] 🛡️ Action: Broadcasting block to ALL AWS Network ACLs...")
        try:
            # 1. Fetch ALL NACLs in the region
            nacl_response = self.client.describe_network_acls()
            if not nacl_response['NetworkAcls']:
                return {"status": "FAILED", "action": "NO_NACL_FOUND", "provider": "aws"}

            success_count = 0
            
            # 2. Loop through every firewall and lock them down
            for nacl in nacl_response['NetworkAcls']:
                nacl_id = nacl['NetworkAclId']
                existing_rules = nacl['Entries']
                used_numbers = [rule['RuleNumber'] for rule in existing_rules]

                # Check if already blocked on this specific firewall
                already_blocked = False
                for rule in existing_rules:
                    if rule.get('CidrBlock') == f"{attacker_ip}/32" and rule.get('RuleAction') == 'deny':
                        already_blocked = True
                        break

                if already_blocked:
                    print(f"    [AWS-NACL] ⚡ IP {attacker_ip} already blocked in {nacl_id}. Skipping.")
                    success_count += 1
                    continue

                # Find next available rule number
                rule_number = 1
                while rule_number in used_numbers:
                    rule_number += 1

                if rule_number < 32000:
                    self.client.create_network_acl_entry(
                        NetworkAclId=nacl_id,
                        RuleNumber=rule_number,
                        Protocol='-1', 
                        RuleAction='deny',
                        Egress=False,  
                        CidrBlock=f"{attacker_ip}/32"
                    )
                    print(f"    [AWS-NACL] 🚫 DENY INBOUND: {attacker_ip} ACTIVE on {nacl_id}.")
                    success_count += 1

            if success_count > 0:
                return {"status": "SUCCESS", "action": "GLOBAL_NACL_BLOCK", "provider": "aws"}
            else:
                return {"status": "FAILED", "action": "NACL_UPDATE_ERROR", "provider": "aws"}
                
        except Exception as e:
            print(f"    [AWS-NACL] ⚠️ NACL update failed: {e}")
            return {"status": "FAILED", "action": "NACL_UPDATE_ERROR", "provider": "aws"}

    def isolate_instance(self, incident: Dict) -> bool:
        print(f"[AWS] Isolating instance {incident.get('node_id')}")
        return True