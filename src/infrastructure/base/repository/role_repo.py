from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, Optional
import src.domain as domain


@dataclass
class BaseRoleRepository(ABC):
    @abstractmethod
    async def get_role_by_id(self, role_id: str) -> domain.Role:
        raise NotImplementedError

    @abstractmethod
    async def get_all_roles(self) -> Iterable[domain.Role]:
        raise NotImplementedError

    @abstractmethod
    async def create_role(self, role: domain.Role) -> domain.Role:
        raise NotImplementedError

    async def update_role(self, role: domain.Role) -> Optional[domain.Role]:
        raise NotImplementedError

    async def delete_role(self, role_id: str) -> None:
        raise NotImplementedError

    async def set_role_permissions(
        self, role_id: str, permissions: Iterable[domain.Permission]
    ) -> None:
        raise NotImplementedError

    async def get_role_permissions(self, role_id: str) -> Iterable[domain.Permission]:
        raise NotImplementedError

    async def get_role_by_name(self, name: str) -> Optional[domain.Role]:
        raise NotImplementedError
