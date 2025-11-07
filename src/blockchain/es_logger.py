import os
import json
import logging
from elasticsearch import Elasticsearch

# --- Configuration ---
# Use the service name defined in docker-compose.yml to ensure connectivity inside Docker
ES_HOST = os.getenv("ELASTICSEARCH_HOSTS", "http://elasticsearch-1:9200")
INDEX_NAME = "hawkgrid-forensics"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_to_elasticsearch(data: dict) -> bool:
    """
    Connects to Elasticsearch and indexes the final forensic incident report.
    This makes the data searchable and viewable in Kibana.
    Returns True on successful indexing, False on failure.
    """
    try:
        # 1. Connect to Elasticsearch container
        # Note: The Orchestrator container can reach the ES container using its service name (elasticsearch-1)
        es = Elasticsearch([ES_HOST], timeout=5)
        
        # Verify connection (optional but good practice)
        if not es.ping():
             logging.error("ES connection failed: Cannot ping the cluster.")
             return False
        
        # 2. Prepare the document for indexing
        # Ensure the Kibana time field is present, converting timestamp object to string/ISO format
        data['@timestamp'] = data.get('timestamp') 
        
        # 3. Index the document
        response = es.index(
            index=INDEX_NAME, 
            document=data
        )
        
        logging.info(f"Forensic report indexed. ES ID: {response['_id']}")
        return True
        
    except Exception as e:
        logging.error(f"Error indexing to Elasticsearch: {e}")
        return False

if __name__ == '__main__':
    # This block is for simple testing if run outside the FastAPI app
    print("Elasticsearch logger module created and ready for import.")
