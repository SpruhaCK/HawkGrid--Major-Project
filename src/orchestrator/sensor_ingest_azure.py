import os
import json
import requests
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv(find_dotenv())


def ingest_azure_logs():
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_CONTAINER_NAME")
    target_vm_ip = os.getenv("TARGET_VM_IP", "10.0.1.5")
    audit_file = "forensic_audit.json"

    if not connection_string or not container_name:
        print("Missing AZURE_STORAGE_CONNECTION_STRING or AZURE_CONTAINER_NAME environment variables.")
        return

    try:
        service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = service_client.get_container_client(container_name)

        now = datetime.utcnow()
        current_date_path = now.strftime('y=%Y/m=%m/d=%d')
        hours_to_check = [f"h={now.strftime('%H')}", f"h={(now - timedelta(hours=1)).strftime('%H')}"]

        print(f"--- Forensic Ingest Active [{now.strftime('%Y-%m-%d %H:%M:%S')} UTC] ---")

        blobs = container_client.list_blobs(name_starts_with="resourceId=/")

        audit_entries = []
        total_alerts_sent = 0

        for blob in blobs:
            try:
                if current_date_path in blob.name and any(hr in blob.name for hr in hours_to_check):
                    print(f"Reading Azure Log: {blob.name.split('/')[-1]}")

                    blob_client = container_client.get_blob_client(blob.name)
                    content = blob_client.download_blob().readall()
                    try:
                        log_data = json.loads(content)
                    except TypeError:
                        log_data = json.loads(content.decode('utf-8'))

                    for record in log_data.get("records", []):
                        properties = record.get("properties", {})
                        for flow_rule in properties.get("flows", []):
                            for flow_data in flow_rule.get("flows", []):
                                for tuple_str in flow_data.get("flowTuples", []):
                                    parts = tuple_str.split(',')
                                    if len(parts) < 8:
                                        continue

                                    # If destination IP matches our target
                                    if parts[2] == target_vm_ip:
                                        payload = {
                                            "timestamp": record.get("time"),
                                            "source_ip": parts[1],
                                            "destination_ip": parts[2],
                                            "port": parts[4],
                                            "protocol": "TCP" if parts[5] == "T" else "UDP",
                                            "action": "Allowed" if parts[7] == "A" else "Denied",
                                        }

                                        audit_entries.append(payload)

                                        # Send to Orchestrator for ML Classification (best-effort)
                                        try:
                                            requests.post("http://127.0.0.1:8000/detect", json=payload, timeout=2)
                                            total_alerts_sent += 1
                                        except Exception:
                                            pass
            except Exception as e:
                print(f"Warning: failed to process blob {getattr(blob, 'name', '<unknown>')}: {e}")

        # 2. Write directly to forensic_audit.json
        if audit_entries:
            if os.path.exists(audit_file):
                with open(audit_file, "r") as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        existing_data = []
            else:
                existing_data = []

            existing_data.extend(audit_entries)

            with open(audit_file, "w") as f:
                json.dump(existing_data, f, indent=4)

            print(f"Success: {len(audit_entries)} incidents written to {audit_file} (alerts sent: {total_alerts_sent})")
        else:
            print("No new matching activity found in the checked Azure logs.")

    except Exception as e:
        print(f"Error while ingesting Azure logs: {e}")


if __name__ == "__main__":
    ingest_azure_logs()