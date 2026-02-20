from abc import ABC, abstractmethod
from typing import Dict, List


class CloudProvider(ABC):

    @abstractmethod
    def discover_assets(self) -> List[Dict]:
        """Return list of assets with public/private IP"""
        pass

    @abstractmethod
    def resolve_private_ip(self, public_ip: str) -> str:
        """Resolve public IP to private IP"""
        pass

    @abstractmethod
    def isolate_instance(self, incident: Dict) -> bool:
        """Apply containment to instance"""
        pass