import os
import logging
import boto3
from botocore.exceptions import ClientError

# ----------------------------
# OPTIONAL AZURE SUPPORT
# ----------------------------
# try:
#     from azure.identity import AzureCliCredential
#     from azure.mgmt.network import NetworkManagementClient
#     AZURE_SDK_AVAILABLE = True
# except ImportError:
#     AZURE_SDK_AVAILABLE = False

# ----------------------------
# LOGGING
# ----------------------------
log = logging.getLogger("hawkgrid-playbook")
log.setLevel(logging.INFO)

# ----------------------------
# CONFIG
# ----------------------------
USE_SIMULATION = os.getenv("USE_SIMULATION", "true").lower() == "true"

# AZURE_DENY_RULE_NAME = "HAWKGRID-DENY-ALL-EGRESS"
# AZURE_RULE_PRIORITY = 100

# ----------------------------
# MOCK ASSET DATABASE
# ----------------------------
ASSET_DATABASE = {
    "10.0.1.90": {  # Use your Linux VM's actual internal IP
        "name": "HawkGrid-Linux-Victim",
        "cloud": "aws",
        "instance_id": "i-033a0ffd99ca7f434",
        "nsg_id": "sg-0076e8e881ba50058"
    },
    "10.0.1.30": {  # Use your Windows VM's actual internal IP
        "name": "HawkGrid-Windows-Victim",
        "cloud": "aws",
        "instance_id": "i-05b17510751c58c59",
        "nsg_id": "sg-0076e8e881ba50058"
    }
    # "Azure-VM-A": {
    #     "cloud": "azure",
    #     "resource_group": "HawkGrid-Prod-RG",
    #     "nsg_name": "vm-a-nsg"
    # }
}

# =====================================================
# CENTRAL PLAYBOOK DISPATCHER
# =====================================================
def execute_playbook(action: str, incident_data: dict) -> dict:
    node_id = incident_data.get("node_id", "unknown-node")

    log.info(
        "Executing playbook '%s' for node '%s'",
        action,
        node_id
    )

    asset = ASSET_DATABASE.get(node_id)

    # -------------------------------------------------
    # CASE 1: UNKNOWN ASSET (DEMO / OBSERVE MODE)
    # -------------------------------------------------
    if not asset:
        log.warning(
            "Unknown asset '%s' — executing simulated containment",
            node_id
        )
        return {
            "playbook_name": action,
            "status": "SIMULATED_SUCCESS",
            "node_id": node_id,
            "mode": "DEMO",
            "details": "Asset not registered. Advisory containment issued."
        }

    # -------------------------------------------------
    # CASE 2: EXPLICIT SIMULATION MODE
    # -------------------------------------------------
    if USE_SIMULATION:
        log.warning(
            "SIMULATION MODE ENABLED — no real action taken for '%s'",
            node_id
        )
        return {
            "playbook_name": action,
            "status": "SIMULATED_SUCCESS",
            "node_id": node_id,
            "mode": "SIMULATION",
            "details": f"Simulated '{action}' executed successfully."
        }

    # -------------------------------------------------
    # CASE 3: REAL ACTION
    # -------------------------------------------------
    try:
        if action != "AUTOMATED_CONTAINMENT":
            raise ValueError(f"Unsupported playbook action: {action}")

        if asset["cloud"] == "aws":
            success = _isolate_aws_node(asset)
        # elif asset["cloud"] == "azure":
        #     success = _isolate_azure_node(asset)
        else:
            raise ValueError(f"Unknown cloud provider: {asset['cloud']}")

        if not success:
            raise RuntimeError("Containment action failed")

        return {
            "playbook_name": action,
            "status": "REAL_ACTION_SUCCESS",
            "node_id": node_id,
            "mode": "REAL",
            "details": "Containment successfully applied."
        }

    except Exception as e:
        log.exception("Playbook execution failed")
        return {
            "playbook_name": action,
            "status": "REAL_ACTION_FAILED",
            "node_id": node_id,
            "mode": "REAL",
            "details": str(e)
        }

# =====================================================
# CLOUD-SPECIFIC ACTIONS
# =====================================================
def _isolate_aws_node(asset: dict, incident_data: dict) -> bool:
    """
    Revised AWS isolation.
    Instead of just revoking egress, we target the specific attacker IP.
    """
    attacker_ip = incident_data.get("src_ip")
    log.info(f"Attempting AWS isolation for attacker {attacker_ip} on {asset['name']}")

    try:
        ec2 = boto3.client("ec2")
        
        # PRO TIP: For a final project, revoking INGRESS is what stops the attack.
        # This removes the permission for that specific IP to hit your ports.
        ec2.revoke_security_group_ingress(
            GroupId=asset["nsg_id"],
            IpPermissions=[{
                "IpProtocol": "-1", # All protocols
                "FromPort": 0,
                "ToPort": 65535,
                "IpRanges": [{"CidrIp": f"{attacker_ip}/32"}] # Block just the attacker
            }]
        )

        log.critical(f"AWS CONTAINMENT SUCCESS — {attacker_ip} blocked on {asset['nsg_id']}")
        return True

    except ClientError as e:
        log.error(f"AWS isolation failed: {e}")
        return False


# def _isolate_azure_node(asset: dict) -> bool:
#     if not AZURE_SDK_AVAILABLE:
#         log.error("Azure SDK not installed")
#         return False

#     try:
#         credential = AzureCliCredential()
#         subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
#         if not subscription_id:
#             raise ValueError("AZURE_SUBSCRIPTION_ID not set")

#         client = NetworkManagementClient(
#             credential,
#             subscription_id
#         )

#         rule = {
#             "protocol": "*",
#             "source_address_prefix": "*",
#             "destination_address_prefix": "Internet",
#             "source_port_range": "*",
#             "destination_port_range": "*",
#             "access": "Deny",
#             "priority": AZURE_RULE_PRIORITY,
#             "direction": "Outbound",
#             "description": "HAWKGRID AUTOMATED ISOLATION"
#         }

#         client.security_rules.begin_create_or_update(
#             asset["resource_group"],
#             asset["nsg_name"],
#             AZURE_DENY_RULE_NAME,
#             rule
#         ).result()

#         log.critical(
#             "AZURE CONTAINMENT SUCCESS — rule applied to %s",
#             asset["nsg_name"]
#         )
#         return True

#     except Exception as e:
#         log.error("Azure isolation failed: %s", e)
#         return False
