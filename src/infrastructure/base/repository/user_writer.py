from abc import ABC, abstractmethod
from dataclasses import dataclass

import src.domain.user.entity.user as domain


@dataclass
class BaseUserWriter(ABC):
    @abstractmethod
    async def create_user(self, user: domain.User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_user(self, user: domain.User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def check_if_field_exists(self, field: str, value: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def check_user_has_permission(
        self, user_id: str, permission_name: str
    ) -> bool:
        raise NotImplementedError
