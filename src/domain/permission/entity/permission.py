from dataclasses import dataclass

from src.domain.base.entity.base import BaseEntity
from src.domain.permission.values.permission_name import PermissionName


@dataclass(eq=False)
class Permission(BaseEntity):
    permission_name: PermissionName
