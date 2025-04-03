from dataclasses import dataclass
from typing import Protocol, Optional, Iterable
from abc import abstractmethod, ABC
import src.domain.user.entity.user as domain
import src.infrastructure.db.models.user as models


@dataclass
class BaseUserWriter(ABC):
    @abstractmethod
    async def create_user(self, user: domain.User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_user(self, user: domain.User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set_user_roles(
        self, user_id: str, role: Optional[Iterable[domain.Role] | domain.Role] = None
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def check_if_field_exists(self, field: str, value: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def check_user_has_permission(
        self, user_id: str, permission_name: str
    ) -> bool:
        raise NotImplementedError
