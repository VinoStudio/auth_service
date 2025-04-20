from abc import ABC, abstractmethod
from typing import List, Any, Optional
import src.domain as domain


class BasePermissionRepository(ABC):
    @abstractmethod
    async def create_permission(
        self,
        permission: domain.Permission,
    ) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_permission_by_id(self, permission_id: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_permission_by_name(self, permission_name: str) -> Any:
        raise NotImplementedError

    # @abstractmethod
    # async def get_role_permissions(self, role_id: str) -> Any:
    #     raise NotImplementedError

    @abstractmethod
    async def get_existing_permissions(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_all_permissions(self, pagination: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def check_permission_exists(self, permission_name: str) -> Any:
        raise NotImplementedError
