from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLedger(ABC):
    """
    Abstract ledger interface.
    All ledger backends must implement this.
    """

    @abstractmethod
    def log_incident(self, incident: Dict[str, Any], response_action: str) -> Dict[str, Any]:
        pass