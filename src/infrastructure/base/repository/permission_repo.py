from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING

from src import domain
from src.infrastructure.db import models

if TYPE_CHECKING:
    from src.infrastructure.repositories.pagination import Pagination


class BasePermissionRepository(ABC):
    @abstractmethod
    async def create_permission(
        self, permission: domain.Permission
    ) -> models.Permission | None:
        """Create a new Permission from entity"""
        raise NotImplementedError

    @abstractmethod
    async def delete_permission(self, permission_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_permission_by_id(
        self, permission_id: str
    ) -> domain.Permission | None:
        """Get a permission by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_permission_by_name(
        self, permission_name: str
    ) -> domain.Permission | None:
        """Get roles by name"""
        raise NotImplementedError

    @abstractmethod
    async def get_permission_roles(self, permission_id: str) -> list[domain.Role]:
        raise NotImplementedError

    @abstractmethod
    async def get_existing_permissions(self) -> Sequence[models.Permission]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_permissions(
        self, pagination: "Pagination"
    ) -> Iterable[domain.Permission]:
        raise NotImplementedError

    @abstractmethod
    async def check_permission_exists(self, permission_name: str) -> bool:
        """Check if a role exists"""
        raise NotImplementedError

    @abstractmethod
    async def count_roles_with_permission(self, permission_name: str) -> int:
        raise NotImplementedError
