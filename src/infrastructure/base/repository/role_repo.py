from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, Optional, Any, List
import src.domain as domain


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
    async def set_role_permission(self, role_id: str, permission_id: str) -> Any:
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

    @abstractmethod
    async def get_roles_with_metrics(self) -> Any:
        raise NotImplementedError

    @staticmethod
    def get_role():
        pass

    @staticmethod
    def get_permission():
        pass
