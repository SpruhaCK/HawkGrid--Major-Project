import os
import time
import logging
from src.cloud.provider_factory import get_cloud_providers

logger = logging.getLogger("hawkgrid-realtime")

class RealtimeSensor:
    def __init__(self):
        # This will securely load only the clouds that are UP and running VMs
        self.providers = get_cloud_providers().values()

    def start_polling(self, callback_func, interval=5):
        """Polls all configured active clouds for new security logs."""
        cloud_names = [p.name for p in self.providers]
        logger.info(f"Starting real-time sensor for active providers: {cloud_names}")
        
        if not self.providers:
            logger.warning("No active providers to poll. Exiting sensor loop.")
            return

        try:
            while True:
                for provider in self.providers:
                    # Note: We need to ensure fetch_logs() is added to your base_provider.py!
                    if hasattr(provider, 'fetch_logs'):
                        logs = provider.fetch_logs()
                        
                        if logs:
                            logger.info(f"Ingested {len(logs)} logs from {provider.name.upper()}")
                            for log_event in logs:
                                callback_func(log_event)
                    else:
                        logger.debug(f"{provider.name.upper()} does not implement fetch_logs(). Skipping.")
                            
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Sensor polling stopped.")