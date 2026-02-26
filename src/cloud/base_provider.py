from abc import ABC, abstractmethod
from typing import Dict, List

class CloudProvider(ABC):
    name: str

    @abstractmethod
    def discover_assets(self) -> List[Dict]:
        pass

    @abstractmethod
    def resolve_private_ip(self, public_ip: str) -> str:
        pass

    @abstractmethod
    def isolate_instance(self, incident: Dict) -> bool:
        pass

    @abstractmethod
    def block_ip(self, attacker_ip: str) -> dict:
        pass