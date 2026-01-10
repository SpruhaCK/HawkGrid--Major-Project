"""
playbook.py

Contains the "Tactical Incident Response" logic.
This module is responsible for orchestrating the *response* to a
detected anomaly (e.g., isolating a node).

It is designed to be multi-cloud and fail-safe, with a simulation
mode for local development.
"""
import os
import logging
import boto3
from botocore.exceptions import ClientError

# --- Mock Azure/AWS clients for simulation ---
# We will add the real Azure/AWS clients here later.
# For now, we simulate them.
try:
    from azure.identity import AzureCliCredential
    from azure.mgmt.network import NetworkManagementClient
    AZURE_SDK_AVAILABLE = True
except ImportError:
    AZURE_SDK_AVAILABLE = False
    logging.warning("Azure SDK not installed. Azure actions will be simulated.")
# --- End Mock ---


# Set up logging
log = logging.getLogger("hawkgrid-playbook")
log.setLevel(logging.INFO)

# --- CONFIGURATION ---
# Read the simulation flag from environment variables.
# This is set in docker-compose.yml for local dev.
USE_SIMULATION = os.getenv("USE_SIMULATION", "false").lower() == "true"

# Define the features for the high-priority DENY rule
AZURE_DENY_RULE_NAME = "HAWKGRID-DENY-ALL-EGRESS"
AZURE_RULE_PRIORITY = 100 # High priority to override other rules

# This is a simple mock "Asset Database"
# In a real project, this would be a real database (e.g., DynamoDB)
# It maps a node_id to the cloud provider and its specific resource details.
ASSET_DATABASE = {
    "AWS-EC2-B": {
        "cloud": "aws",
        "instance_id": "i-12345abcdef",
        "nsg_id": "sg-0abcdef123" # AWS Network Security Group (Security Group)
    },
    "Azure-VM-A": {
        "cloud": "azure",
        "resource_group": "HawkGrid-Prod-RG",
        "nsg_name": "vm-a-nsg" # Azure Network Security Group
    }
}

# --- CENTRAL PLAYBOOK DISPATCHER ---

def execute_playbook(action: str, incident_data: dict) -> dict:
    """
    Central dispatcher for all incident response actions.
    It reads the 'action' and 'incident_data' and routes
    to the correct function (e.g., AWS, Azure, or simulation).
    """
    log.info(f"Executing playbook '{action}' for node '{incident_data.get('node_id')}'")
    
    # 1. Get asset details from our "database"
    node_id = incident_data.get("node_id")
    asset = ASSET_DATABASE.get(node_id)

    # --- THIS IS THE FIX ---
    # 2. Check for unknown asset *before* simulation
    # If the asset isn't in our database, we can't act on it.
    if not asset:
        log.error(f"Playbook failed: Node ID '{node_id}' not found in Asset Database.")
        return {
            "playbook_name": action,
            "status": "failed",
            "node_id": node_id,
            "details": f"Node ID '{node_id}' is not a known asset."
        }

    # 3. Check if we are in simulation mode
    if USE_SIMULATION:
        log.warning(f"SIMULATION MODE: Not taking real action for '{node_id}'.")
        return {
            "playbook_name": action,
            "status": "simulated_success",
            "node_id": node_id,
            "details": f"Simulated action '{action}' for node '{node_id}'."
        }

    # 4. If not in simulation, route to the correct cloud provider
    try:
        if action == "AUTOMATED_CONTAINMENT":
            if asset["cloud"] == "aws":
                success = _isolate_aws_node(asset)
            elif asset["cloud"] == "azure":
                success = _isolate_azure_node(asset)
            else:
                raise ValueError(f"Unknown cloud provider: {asset['cloud']}")

            if success:
                return {
                    "playbook_name": action,
                    "status": "real_action_success",
                    "node_id": node_id,
                    "details": f"Successfully applied containment rule to {node_id}."
                }
            else:
                raise Exception("Containment action failed to apply.")

    except Exception as e:
        log.exception(f"REAL ACTION FAILED for playbook '{action}' on node '{node_id}': {e}")
        return {
            "playbook_name": action,
            "status": "real_action_failed",
            "node_id": node_id,
            "details": str(e)
        }

# --- CLOUD-SPECIFIC ACTIONS ---

def _isolate_aws_node(asset: dict) -> bool:
    """Isolates an AWS EC2 instance by modifying its Security Group."""
    log.info(f"Attempting REAL AWS isolation for instance '{asset['instance_id']}' using NSG '{asset['nsg_id']}'")
    
    try:
        # Boto3 will automatically use credentials from the environment
        ec2 = boto3.client('ec2')
        
        # This rule revokes all outbound traffic (0.0.0.0/0)
        # This is a destructive action, perfect for containment.
        ec2.revoke_security_group_egress(
            GroupId=asset['nsg_id'],
            IpPermissions=[
                {
                    'IpProtocol': '-1', # All protocols
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                }
            ]
        )
        log.critical(f"SUCCESS: Revoked all egress from AWS NSG: {asset['nsg_id']}")
        return True
        
    except ClientError as e:
        log.error(f"Failed to isolate AWS node: {e}")
        return False

def _isolate_azure_node(asset: dict) -> bool:
    """Isolates an Azure VM by modifying its Network Security Group."""
    log.info(f"Attempting REAL Azure isolation for NSG '{asset['nsg_name']}' in RG '{asset['resource_group']}'")

    if not AZURE_SDK_AVAILABLE:
        log.error("Cannot isolate Azure node: Azure SDK is not installed.")
        return False
        
    try:
        # 1. Authenticate
        credential = AzureCliCredential()
        subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
        if not subscription_id:
            raise ValueError("AZURE_SUBSCRIPTION_ID environment variable is not set.")

        network_client = NetworkManagementClient(credential, subscription_id)

        # 2. Define the new DENY rule
        security_rule = {
            'protocol': '*',
            'source_address_prefix': '*', # Any source
            'destination_address_prefix': 'Internet', # To the internet
            'source_port_range': '*',
            'destination_port_range': '*',
            'access': 'Deny',
            'priority': AZURE_RULE_PRIORITY,
            'direction': 'Outbound',
            'description': 'HAWKGRID: AUTOMATED ANOMALY ISOLATION'
        }

        # 3. Apply the rule
        network_client.security_rules.begin_create_or_update(
            asset['resource_group'],
            asset['nsg_name'],
            AZURE_DENY_RULE_NAME,
            security_rule
        ).result() # .result() waits for the operation to complete

        log.critical(f"SUCCESS: Applied isolation rule '{AZURE_DENY_RULE_NAME}' to Azure NSG: {asset['nsg_name']}")
        return True

    except Exception as e:
        log.error(f"Failed to isolate Azure node: {e}")
        return False