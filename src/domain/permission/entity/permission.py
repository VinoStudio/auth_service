from dataclasses import dataclass, field
from src.domain.base.entity.base import BaseEntity
from src.domain.permission.values.permission_name import PermissionName
from uuid6 import uuid7


@dataclass
class Permission(BaseEntity):
    id: str = field(default_factory=lambda: str(uuid7()), kw_only=True)
    permission_name: PermissionName

    def __eq__(self, other):
        if not isinstance(other, Permission):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
