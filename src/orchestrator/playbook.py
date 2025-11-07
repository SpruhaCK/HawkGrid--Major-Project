import os
import logging
from azure.identity import AzureCliCredential
from azure.mgmt.network import NetworkManagementClient

# Define the features for the high-priority DENY rule
PRIORITY = 100 
DENY_RULE_NAME = "HAWKGRID-ANOMALY-DENY-ALL"

def isolate_compromised_node(resource_group_name: str, network_security_group_name: str):
    """
    Connects to Azure and modifies the Network Security Group (NSG) to block
    all outbound traffic, effectively isolating the node.
    """
    logging.info(f"Attempting to connect to Azure and modify NSG: {network_security_group_name}")
    
    # 1. AUTHENTICATION (Using CLI credentials for simple project demo)
    try:
        # The Orchestrator must be logged into Azure via 'az login' on the host
        # or configured with a service principal (which is best practice)
        credential = AzureCliCredential()
        
        # NOTE: You must set your SUBSCRIPTION_ID environment variable
        subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
        if not subscription_id:
            logging.error("AZURE_SUBSCRIPTION_ID environment variable is not set.")
            raise ValueError("AZURE_SUBSCRIPTION_ID missing.")

        network_client = NetworkManagementClient(credential, subscription_id)
        
    except Exception as e:
        logging.error(f"Azure authentication or client creation failed: {e}")
        # Return False to indicate the real action failed, triggering local fallback
        return False

    # 2. Define the new DENY rule object
    security_rule = {
        'protocol': '*',
        'source_address_prefix': 'Internet',
        'destination_address_prefix': '*',
        'source_port_range': '*',
        'destination_port_range': '*',
        'access': 'Deny',
        'priority': PRIORITY,
        'direction': 'Outbound',
        'description': 'HAWKGRID: AUTOMATED ANOMALY ISOLATION - DENY ALL EGRESS'
    }

    # 3. Apply the rule to the NSG
    try:
        # Use begin_create_or_update to apply the change asynchronously
        # This modification is designed to deny all OUTBOUND traffic from the VM
        # to the outside world, effectively containing the threat.
        network_client.security_rules.begin_create_or_update(
            resource_group_name,
            network_security_group_name,
            DENY_RULE_NAME,
            security_rule
        ).result() # .result() waits for the operation to complete
        
        logging.critical(f"SUCCESS: Isolation Rule '{DENY_RULE_NAME}' applied to {network_security_group_name}")
        return True

    except Exception as e:
        logging.error(f"FAILED to update NSG {network_security_group_name}. Error: {e}")
        return False


if __name__ == '__main__':
    # Placeholder values for local testing:
    RG_NAME = "HawkGrid-RG-Test"
    NSG_NAME = "HawkGrid-NSG-Test"
    
    # NOTE: This requires a live Azure environment and 'az login' to work!
    # result = isolate_compromised_node(RG_NAME, NSG_NAME)
    # print(f"Simulation Isolation Result: {result}")
    
    print("Playbook file is ready for Azure integration.")
    