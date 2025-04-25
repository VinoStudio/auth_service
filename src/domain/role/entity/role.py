from dataclasses import dataclass, field
from datetime import datetime, UTC

from src.domain.base.entity.base import BaseEntity
from src.domain.permission.entity.permission import Permission
from src.domain.role.values.role_name import RoleName
from typing import Set, FrozenSet
from uuid6 import uuid7


@dataclass
class Role(BaseEntity):
    id: str = field(default_factory=lambda: str(uuid7()), kw_only=True)
    name: RoleName
    description: str = field(default="", kw_only=True)
    security_level: int
    _permissions: Set[Permission] = field(default_factory=set)

    @property
    def permission(self) -> FrozenSet[Permission]:
        return frozenset(self._permissions)

    def add_permission(self, permission: Permission) -> None:
        self._permissions.add(permission)

    def remove_permission(self, permission: Permission) -> None:
        self._permissions.discard(permission)

    def __eq__(self, other):
        if not isinstance(other, Role):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
