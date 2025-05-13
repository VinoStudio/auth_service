from dataclasses import dataclass, field

from src.domain.base.entity.base import BaseEntity
from src.domain.permission.entity.permission import Permission
from src.domain.role.values.role_name import RoleName


@dataclass
class Role(BaseEntity):
    name: RoleName
    description: str = field(default="", kw_only=True)
    security_level: int
    _permissions: set[Permission] = field(default_factory=set)

    @property
    def permission(self) -> frozenset[Permission]:
        return frozenset(self._permissions)

    def add_permission(self, permission: Permission) -> None:
        self._permissions.add(permission)

    def remove_permission(self, permission: Permission) -> None:
        self._permissions.discard(permission)
