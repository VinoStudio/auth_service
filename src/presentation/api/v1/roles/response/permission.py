from typing import List
from pydantic import BaseModel, Field

import src.domain as domain


class CreatedPermissionResponseSchema(BaseModel):
    permission_name: str

    @classmethod
    def from_entity(cls, permission: domain.Permission):
        return cls(permission_name=permission.permission_name.to_raw())


class GetPermissionsResponseSchema(BaseModel):
    permissions: List[str]

    @classmethod
    def from_entity(cls, permissions: List[domain.Permission]):
        return cls(permissions=[p.permission_name.to_raw() for p in permissions])
