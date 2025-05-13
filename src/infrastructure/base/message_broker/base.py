from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class MessageBroker(ABC):
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the message broker."""
