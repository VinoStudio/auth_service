from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from src import domain

if TYPE_CHECKING:
    from src.infrastructure.repositories.pagination import Pagination


@dataclass
class BaseRoleRepository(ABC):
    @abstractmethod
    async def create_role(self, role: domain.Role) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def update_role(self, role: domain.Role) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_role_by_id(self, role_id: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_role_by_name(self, name: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_all_roles(self, pagination: "Pagination") -> Any:
        raise NotImplementedError

    @abstractmethod
    async def update_role_name(self, role_id: str, name: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def delete_role(self, role_id: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_role_permissions(self, role_id: str) -> Any:
        raise NotImplementedError

    async def get_existing_roles(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_users_with_role(self, role_id: str, pagination: "Pagination") -> Any:
        raise NotImplementedError

    @abstractmethod
    async def check_role_exists(self, role_name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def count_users_with_role(self, role_name: str) -> int:
        raise NotImplementedError
