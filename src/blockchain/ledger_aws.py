import boto3
import json
import logging
import time
from pyqldb.driver.qldb_driver import QldbDriver
from pyqldb.errors import ExecuteError, DriverClosedError, SessionPoolEmptyError

LEDGER_NAME = "hawkgrid-forensic-ledger"
TABLE_NAME = "incidents"
log = logging.getLogger("hawkgrid-ledger-aws")
log.setLevel(logging.INFO)

# Global QLDB Driver instance for session reuse
qldb_driver = None

def _create_table_if_not_exists(driver: QldbDriver, table_name: str):
    """
    Ensures the forensic table exists in QLDB. 
    This is critical for 'Zero-Touch' deployment.
    """
    log.info(f"Checking if table '{table_name}' exists...")
    try:
        table_names = list(driver.list_tables())
        if table_name in table_names:
            log.info(f"Table '{table_name}' already exists.")
            return
        
        log.warning(f"Table '{table_name}' not found. Creating table...")
        
        def create_table_txn(transaction_executor):
            transaction_executor.execute_statement(f"CREATE TABLE {table_name}")

        driver.execute_lambda(create_table_txn)
        log.info(f"Successfully created table '{table_name}'.")

    except ExecuteError as e:
        log.error(f"PartiQL error during table creation: {e}")
        raise
    except Exception as e:
        log.exception(f"Unexpected error creating table '{table_name}': {e}")
        raise

def get_qldb_driver():
    """Initializes the QLDB driver with the correct ledger name."""
    global qldb_driver
    if qldb_driver is None:
        log.info(f"Initializing QLDB Driver for ledger: {LEDGER_NAME}")
        try:
            # The driver uses your 'aws configure' credentials automatically
            qldb_driver = QldbDriver(ledger_name=LEDGER_NAME)
            
            # Verify table existence before processing any traffic
            _create_table_if_not_exists(qldb_driver, TABLE_NAME)
            
        except Exception as e:
            log.exception(f"Failed to initialize QLDB Driver: {e}")
            raise
    return qldb_driver

def log_incident_to_ledger(incident_data: dict, response_action: str) -> dict:
    """
    Writes a cryptographic record of the anomaly to the ledger.
    This fulfills the 'Forensic Integrity' objective.
    """
    try:
        driver = get_qldb_driver()
    except Exception as e:
        log.error(f"Ledger initialization failed. Data will not be immutable: {e}")
        raise 
    
    # 1. Standardize the Forensic Block
    incident_details = {
        "incident_time": incident_data.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())),
        "node_id": incident_data.get("node_id"),
        "cloud_provider": incident_data.get("cloud_provider"),
        "anomaly_score": incident_data.get("anomaly_score"),
        "attack_type": incident_data.get("attack_type", "UNCATEGORIZED_ANOMALY"), 
        "response_action": response_action,
        "raw_event": incident_data.get("raw_event_sample", {}),
        "hawkgrid_version": "1.0-stable"
    }

    try:
        # 2. Define the write function using PartiQL
        def execute_insert(transaction_executor):
            statement = f"INSERT INTO {TABLE_NAME} ?"
            transaction_executor.execute_statement(statement, incident_details)

        # 3. Execute the lambda (handles retries and session management)
        driver.execute_lambda(execute_insert)
        
        log.critical(f"IMMUTABLE LOG CREATED: Node {incident_details['node_id']} flagged.")
        
        return {
            "status": "success",
            "ledger_type": "AWS_QLDB",
            "record": incident_details,
            "verification": "Cryptographic signature pending journal seal"
        }

    except ExecuteError as e:
        log.error(f"Ledger write failed (Check QLDB permissions/IAM): {e}")
        raise
    except (DriverClosedError, SessionPoolEmptyError) as e:
        log.error(f"Ledger session error: {e}")
        raise
    except Exception as e:
        log.exception(f"General failure in ledger component: {e}")
        raise