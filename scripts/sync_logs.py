import os
import json
from src.cloud.provider_factory import get_cloud_providers

def sync_all_logs(output_file="synced_logs.json"):
    """
    Utility script to pull logs from all active clouds and sync them locally.
    """
    print("Initializing cloud providers for log synchronization...")
    
    # This securely fetches only the clouds that are UP and running
    providers = get_cloud_providers()
    all_logs = []

    if not providers:
        print("No active clouds found to sync logs from. Are your instances running?")
        return

    for name, provider in providers.items():
        print(f"Syncing logs from {name.upper()}...")
        
        # Safely checks if the provider has the fetch_logs method
        if hasattr(provider, 'fetch_logs'):
            try:
                logs = provider.fetch_logs()
                if logs:
                    all_logs.extend(logs)
                    print(f"Successfully pulled {len(logs)} logs from {name.upper()}.")
                else:
                    print(f"No new logs found in {name.upper()}.")
            except Exception as e:
                print(f"Error fetching logs from {name.upper()}: {e}")
        else:
            print(f"Provider {name.upper()} does not support log fetching yet.")

    # Save everything to the JSON file
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(all_logs, f, indent=4)
        
    print(f"Sync complete. {len(all_logs)} total logs saved to {output_file}.")

if __name__ == "__main__":
    sync_all_logs()