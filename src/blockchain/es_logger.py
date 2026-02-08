import os
import json
import logging
from elasticsearch import Elasticsearch

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
        es = Elasticsearch([ES_HOST], timeout=5)
        if not es.ping():
             logging.error("ES connection failed: Cannot ping the cluster.")
             return False
            
        data['@timestamp'] = data.get('timestamp') 
        
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
    print("Elasticsearch logger module created and ready for import.")
