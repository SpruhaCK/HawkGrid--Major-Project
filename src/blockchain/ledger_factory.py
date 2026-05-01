import os
import logging
from typing import Optional
from .base_ledger import BaseLedger
from src.blockchain.ledger_local import LocalLedger

log = logging.getLogger("hawkgrid-ledger-factory")

def get_ledger() -> BaseLedger:
    """
    Dynamically selects ledger backend based on environment variable.
    Only imports backend when actually needed.
    """

    ledger_type = os.getenv("HG_LEDGER_TYPE", "local").lower()
    log.info(f"Initializing ledger backend: {ledger_type}")
    
    if ledger_type == "local":
        return LocalLedger()
        
    elif ledger_type == "aws":
        try:
            from .ledger_aws_qldb import AWSQLDBLedger
            return AWSQLDBLedger()
        except ImportError:
            raise RuntimeError(
                "AWS QLDB selected but pyqldb is not installed. "
                "Install with: pip install pyqldb"
            )
            
    elif ledger_type == "azure":
        try:
            from .ledger_azure import AzureConfidentialLedger
            return AzureConfidentialLedger()
        except ImportError:
            raise RuntimeError(
                "Azure Ledger selected but required Azure SDKs are missing. "
                "Install with: pip install azure-identity azure-confidentialledger"
            )

    elif ledger_type == "elasticsearch":
        from .ledger_elasticsearch import ElasticsearchLedger
        return ElasticsearchLedger()

    else:
        raise ValueError(f"Unsupported ledger type: {ledger_type}")