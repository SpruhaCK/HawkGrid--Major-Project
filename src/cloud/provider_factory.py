import os
import logging
from typing import Dict
from src.cloud.base_provider import CloudProvider

log = logging.getLogger("hawkgrid-provider")

def _aws_ready():
    return (
        os.getenv("AWS_REGION") and
        os.getenv("AWS_ACCESS_KEY_ID") and
        os.getenv("AWS_SECRET_ACCESS_KEY")
    )

def _azure_ready():
    return (
        os.getenv("AZURE_SUBSCRIPTION_ID") and
        os.getenv("AZURE_CLIENT_ID") and
        os.getenv("AZURE_CLIENT_SECRET") and
        os.getenv("AZURE_TENANT_ID")
    )

def get_cloud_providers() -> Dict[str, CloudProvider]:
    providers = {}

    # ================= AWS =================
    if _aws_ready():
        try:
            from src.cloud.aws_provider import AWSProvider
            aws = AWSProvider()
            aws.discover_assets()
            providers["aws"] = aws
            log.info("AWS provider READY")

        except Exception as e:
            log.warning(f"AWS provider skipped: {e}")
    else:
        log.info("AWS env not configured")

    # ================= AZURE =================
    if _azure_ready():
        try:
            from src.cloud.azure_provider import AzureProvider
            az = AzureProvider()
            az.discover_assets()
            providers["azure"] = az
            log.info("Azure provider READY")

        except Exception as e:
            log.warning(f"Azure provider skipped: {e}")
    else:
        log.info("Azure env not configured")

    # ================= RESULT =================
    if not providers:
        log.warning("No cloud providers READY. Running standalone mode.")
    else:
        log.info(f"Active providers: {list(providers.keys())}")
    return providers
