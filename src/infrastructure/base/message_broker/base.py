from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Awaitable, Union, Optional


@dataclass
class MessageBroker(ABC):
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the message broker."""
        pass
