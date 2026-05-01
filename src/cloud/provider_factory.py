import os
import logging
from typing import Dict
from src.cloud.base_provider import CloudProvider

log = logging.getLogger("hawkgrid-provider")

def _aws_ready():
    return (
        bool(os.getenv("AWS_REGION")) and
        bool(os.getenv("AWS_ACCESS_KEY_ID")) and
        bool(os.getenv("AWS_SECRET_ACCESS_KEY"))
    )

def _azure_ready():
    return (
        bool(os.getenv("AZURE_SUBSCRIPTION_ID")) and
        bool(os.getenv("AZURE_CLIENT_ID")) and
        bool(os.getenv("AZURE_CLIENT_SECRET")) and
        bool(os.getenv("AZURE_TENANT_ID"))
    )

def get_cloud_providers() -> Dict[str, CloudProvider]:
    providers = {}
    
    # Check which clouds the user actually wants to monitor
    requested_clouds = [c.strip() for c in os.getenv("CLOUD_PROVIDER", "aws,azure").lower().split(",")]
    log.info(f"Checking live status for requested clouds: {requested_clouds}")

    # 1. Probe AWS
    if "aws" in requested_clouds and _aws_ready():
        try:
            from src.cloud.aws_provider import AWSProvider
            aws = AWSProvider()
            assets = aws.discover_assets() # Reach into AWS and count VMs
            
            # 🚨 THE CRITICAL CHECK: Only add AWS if servers are actually running
            if assets: 
                providers[aws.name] = aws
                log.info(f"AWS is UP. Discovered {len(assets)} active EC2 instances.")
            else:
                log.warning("AWS keys found, but ZERO running instances. AWS defense bypassed.")
        except Exception as e:
            log.error(f"AWS probe failed (Check connection or keys): {e}")

    # 2. Probe Azure
    if "azure" in requested_clouds and _azure_ready():
        try:
            from src.cloud.azure_provider import AzureProvider
            az = AzureProvider()
            assets = az.discover_assets() # Reach into Azure and count VMs
            
            # 🚨 THE CRITICAL CHECK: Only add Azure if servers are actually running
            if assets: 
                providers[az.name] = az
                log.info(f"Azure is UP. Discovered {len(assets)} active VMs.")
            else:
                log.warning("Azure keys found, but ZERO running VMs. Azure defense bypassed.")
        except Exception as e:
            log.error(f"Azure probe failed: {e}")

    # 3. Final Verification
    if not providers:
        log.critical("HawkGrid is running blind! No active servers found on any cloud.")
    else:
        log.info(f"Mesh Defense Active for: {list(providers.keys())}")
        
    return providers