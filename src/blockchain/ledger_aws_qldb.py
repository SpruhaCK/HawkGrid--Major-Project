import os
import logging
import time
from typing import Dict, Any

from pyqldb.driver.qldb_driver import QldbDriver
from pyqldb.errors import ExecuteError
from .base_ledger import BaseLedger

log = logging.getLogger("hawkgrid-ledger-aws")

LEDGER_NAME = os.getenv("HG_AWS_LEDGER_NAME", "hawkgrid-forensic-ledger")
TABLE_NAME = os.getenv("HG_AWS_LEDGER_TABLE", "incidents")

_qldb_driver = None


def _get_driver():
    global _qldb_driver
    if _qldb_driver is None:
        log.info(f"Initializing QLDB Driver: {LEDGER_NAME}")
        _qldb_driver = QldbDriver(ledger_name=LEDGER_NAME)
    return _qldb_driver


class AWSQLDBLedger(BaseLedger):

    def log_incident(self, incident: Dict[str, Any], response_action: str) -> Dict[str, Any]:

        driver = _get_driver()

        record = {
            "incident_time": incident.get("timestamp", time.time()),
            "node_id": incident.get("node_id"),
            "cloud_provider": incident.get("cloud_provider"),
            "attack_type": incident.get("attack_type", "UNKNOWN"),
            "response_action": response_action,
            "raw_event": incident,
            "hawkgrid_version": os.getenv("HG_VERSION", "2.0")
        }

        try:
            def insert_txn(tx):
                tx.execute_statement(
                    f"INSERT INTO {TABLE_NAME} ?",
                    record
                )

            driver.execute_lambda(insert_txn)

            log.critical("QLDB immutable record created.")
            return {
                "status": "success",
                "ledger_type": "AWS_QLDB",
                "record": record
            }

        except ExecuteError as e:
            log.exception("QLDB write failed")
            raise