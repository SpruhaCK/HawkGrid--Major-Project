import os
import json
import logging
from typing import Dict, Any
from azure.identity import DefaultAzureCredential
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
from .base_ledger import BaseLedger

log = logging.getLogger("hawkgrid-ledger-azure")

class AzureConfidentialLedger(BaseLedger):
    def __init__(self):
        # Dynamically pull from .env, fallback to your hardcoded UMIT URLs
        self.ledger_name = os.getenv("HG_AZURE_LEDGER_NAME", "UMIT-Hawkgrid-Audit-2026")
        self.ledger_url = os.getenv("HG_AZURE_LEDGER_URL", "https://umit-hawkgrid-audit-2026.confidential-ledger.azure.com")
        self.identity_url = os.getenv("HG_AZURE_IDENTITY_URL", "https://identity.confidential-ledger.core.azure.com/ledgerIdentity/umit-hawkgrid-audit-2026")
        
        log.info(f"Initializing Azure Confidential Ledger: {self.ledger_name}")
        self.credential = DefaultAzureCredential()

        try:
            # 1. Get the ledger's network identity (certificate)
            id_client = ConfidentialLedgerCertificateClient(self.identity_url)
            network_identity = id_client.get_ledger_identity(ledger_id=self.ledger_name)
            
            self.cert_path = "networkcert.pem"
            with open(self.cert_path, "w") as f:
                f.write(network_identity['ledgerTlsCertificate'])

            # 2. Create the Ledger Client
            self.client = ConfidentialLedgerClient(
                endpoint=self.ledger_url, 
                credential=self.credential, 
                ledger_certificate_path=self.cert_path
            )
        except Exception as e:
            log.error(f"Failed to initialize Azure Ledger client: {e}")
            raise

    def log_incident(self, incident: Dict[str, Any], response_action: str) -> Dict[str, Any]:
        """Appends the incident to the immutable Azure ledger."""
        record = {
            "incident": incident,
            "response_action": response_action,
            "hawkgrid_version": os.getenv("HG_VERSION", "2.0")
        }
        
        try:
            # 3. Append the incident log
            entry_poller = self.client.begin_create_ledger_entry({"contents": json.dumps(record)})
            result = entry_poller.result()
            
            log.info(f"Incident logged to Azure Ledger. Transaction ID: {result.get('transactionId')}")
            
            return {
                "status": "success",
                "ledger_type": "AZURE_CONFIDENTIAL_LEDGER",
                "transaction_id": result.get('transactionId'),
                "record": record
            }
            
        except Exception as e:
            log.exception("Azure Ledger write failed")
            raise