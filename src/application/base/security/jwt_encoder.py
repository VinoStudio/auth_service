from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class BaseJWTEncoder(ABC):
    @abstractmethod
    def encode(self, payload: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def decode(self, token: str) -> Dict[str, Any]:
        pass
