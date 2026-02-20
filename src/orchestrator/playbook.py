import logging
from typing import Dict

log = logging.getLogger("hawkgrid-playbook")
log.setLevel(logging.INFO)


def execute_playbook(action: str, incident_data: Dict, provider) -> Dict:
    node_id = incident_data.get("node_id")

    if action != "AUTOMATED_CONTAINMENT":
        return {"status": "UNSUPPORTED_ACTION"}

    try:
        success = provider.isolate_instance(incident_data)

        return {
            "status": "SUCCESS" if success else "FAILED",
            "node_id": node_id
        }

    except Exception as e:
        log.exception("Containment failed")
        return {
            "status": "ERROR",
            "node_id": node_id,
            "error": str(e)
        }