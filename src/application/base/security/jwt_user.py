from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class JWTUserInterface(ABC):
    @abstractmethod
    def get_user_identifier(self) -> str:
        pass

    @abstractmethod
    def get_roles(self) -> List[str]:
        pass

    @abstractmethod
    def get_permissions(self) -> List[str]:
        pass

    def get_device_id(self) -> str | None:
        pass

    def get_security_level(self) -> int | None:
        pass
