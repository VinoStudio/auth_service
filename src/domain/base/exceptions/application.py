from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(eq=False, frozen=True)
class AppException(ABC, Exception):
    @property
    @abstractmethod
    def message(self) -> str:
        return "Application Error"
