from typing import Self

from pydantic import BaseModel

from src import domain


class CreatedPermissionResponseSchema(BaseModel):
    permission_name: str

    @classmethod
    def from_entity(cls, permission: domain.Permission) -> Self:
        return cls(permission_name=permission.permission_name.to_raw())


class GetPermissionsResponseSchema(BaseModel):
    permissions: list[str]

    @classmethod
    def from_entity(cls, permissions: list[domain.Permission]) -> Self:
        return cls(permissions=[p.permission_name.to_raw() for p in permissions])
