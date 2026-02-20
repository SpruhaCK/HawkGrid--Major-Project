import os
import logging
from typing import Dict, Any
from elasticsearch import Elasticsearch
from .base_ledger import BaseLedger
log = logging.getLogger("hawkgrid-ledger-es")
ES_HOST = os.getenv("ELASTICSEARCH_HOSTS", "http://localhost:9200")
INDEX_NAME = os.getenv("HG_ES_INDEX", "hawkgrid-forensics")

class ElasticsearchLedger(BaseLedger):
    def __init__(self):
        self.client = Elasticsearch([ES_HOST])

    def log_incident(self, incident: Dict[str, Any], response_action: str) -> Dict[str, Any]:
        document = {
            **incident,
            "response_action": response_action
        }

        try:
            response = self.client.index(
                index=INDEX_NAME,
                document=document
            )
            log.info("Incident indexed to Elasticsearch.")
            return {
                "status": "success",
                "ledger_type": "ELASTICSEARCH",
                "id": response["_id"]
            }

        except Exception:
            log.exception("Elasticsearch write failed")
            raise