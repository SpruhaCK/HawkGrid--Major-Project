import boto3
import json
import logging
import time
from pyqldb.driver.qldb_driver import QldbDriver
from pyqldb.errors import QldbDriverException

# --- Configuration ---
LEDGER_NAME = "hawkgrid-forensic-ledger"
TABLE_NAME = "incidents"
log = logging.getLogger("hawkgrid-ledger-aws")
log.setLevel(logging.INFO)

# Global QLDB Driver
# We reuse the driver for efficiency
qldb_driver = None

# --- NEW FUNCTION ---
def _create_table_if_not_exists(driver: QldbDriver, table_name: str):
    """Checks if a table exists and creates it if it doesn't."""
    log.info(f"Checking if table '{table_name}' exists...")
    try:
        table_names = list(driver.list_tables())
        if table_name in table_names:
            log.info(f"Table '{table_name}' already exists. No action needed.")
            return
        
        # Table does not exist, create it
        log.warning(f"Table '{table_name}' not found. Creating it now...")
        
        def create_table_txn(transaction_executor):
            transaction_executor.execute_statement(f"CREATE TABLE {table_name}")

        driver.execute_lambda(create_table_txn)
        log.info(f"Successfully created table '{table_name}'.")

    except Exception as e:
        log.exception(f"Error checking or creating table '{table_name}': {e}")
        raise

def get_qldb_driver():
    """Initializes and retrieves the QLDB driver."""
    global qldb_driver
    if qldb_driver is None:
        log.info(f"Initializing QLDB Driver for ledger: {LEDGER_NAME}...")
        try:
            # The driver automatically handles AWS credentials
            qldb_driver = QldbDriver(ledger_name=LEDGER_NAME)
            
            # --- ADDED CALL ---
            # Ensure the "incidents" table exists before returning the driver
            _create_table_if_not_exists(qldb_driver, TABLE_NAME)
            
            log.info("QLDB Driver initialized and table verified.")
        except Exception:
            log.exception("Failed to initialize QLDB Driver!")
            raise
    return qldb_driver

def log_incident_to_ledger(incident_data: dict, response_action: str) -> dict:
    """
    1. Connects to the AWS QLDB Ledger.
    2. Inserts the incident data as a document.
    3. QLDB automatically handles all hashing and chaining.
    """
    # --- MODIFIED --- 
    # Wrapped in try/except to handle driver init failure
    try:
        driver = get_qldb_driver()
    except Exception as e:
        log.exception(f"Failed to get QLDB driver. Aborting log to ledger. Error: {e}")
        raise # Re-raise the exception so api.py can catch it
    
    # 1. Prepare the Data Block
    # QLDB accepts Python dicts directly
    incident_details = {
        "incident_time": incident_data.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())),
        "node_id": incident_data.get("node_id"),
        "cloud_provider": incident_data.get("cloud_provider"),
        "anomaly_score": incident_data.get("anomaly_score"),
        "attack_type": incident_data.get("attack_type", "UNCATEGORIZED_ANOMALY"), 
        "response_action": response_action,
        "raw_event": incident_data.get("raw_event_sample", {})
    }

    log.info(f"Attempting to write to QLDB ledger: {LEDGER_NAME}")

    try:
        # 2. Define the write function
        def execute_insert(transaction_executor):
            log.info(f"Inserting document into table: {TABLE_NAME}...")
            # This is PartiQL, QLDB's query language. It's like SQL for JSON.
            statement = f"INSERT INTO {TABLE_NAME} ?"
            # The driver handles serializing the Python dict
            transaction_executor.execute_statement(statement, incident_details)

        # 3. Execute the transaction
        # execute_lambda handles retries and session management
        driver.execute_lambda(execute_insert)
        
        log.critical(f"Successfully wrote incident to QLDB ledger: {incident_details['node_id']}")
        
        # We don't get a hash back immediately, so we return the logged data
        # The true "hash" is the document ID, which you can query later
        return {
            "status": "logged_to_qldb",
            "ledger": LEDGER_NAME,
            "table": TABLE_NAME,
            "incident_data": incident_details
        }

    except Exception as e:
        log.exception(f"Failed to write to QLDB ledger: {e}")
        raise # Re-raise the exception so api.py can catch it