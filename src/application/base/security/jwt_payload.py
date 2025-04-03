from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Dict, Any


@dataclass(frozen=True)
class BaseJWTPayloadGenerator(ABC):
    @abstractmethod
    def generate(self, user: Any, token_type: Any) -> Dict[str, Any]:
        raise NotImplementedError
