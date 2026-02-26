import json
from azure.identity import DefaultAzureCredential
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient

def log_incident_to_ledger(incident_data):
    # Update these with your specific Azure details
    ledger_name = "UMIT-Hawkgrid-Audit-2026"
    ledger_url = f"https://umit-hawkgrid-audit-2026.confidential-ledger.azure.com"
    identity_url = "https://identity.confidential-ledger.core.azure.com/ledgerIdentity/umit-hawkgrid-audit-2026"

    credential = DefaultAzureCredential()

    # 1. Get the ledger's network identity (certificate)
    id_client = ConfidentialLedgerCertificateClient(identity_url)
    network_identity = id_client.get_ledger_identity(ledger_id=ledger_name)
    
    with open("networkcert.pem", "w") as f:
        f.write(network_identity['ledgerTlsCertificate'])

    # 2. Create the Ledger Client
    client = ConfidentialLedgerClient(
        endpoint=ledger_url, 
        credential=credential, 
        ledger_certificate_path="networkcert.pem"
    )

    # 3. Append the incident log
    entry_poller = client.begin_create_ledger_entry({"contents": json.dumps(incident_data)})
    result = entry_poller.result()
    
    print(f"Incident logged to Azure Ledger. Transaction ID: {result['transactionId']}")
    return result