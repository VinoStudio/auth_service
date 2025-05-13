from typing import Self

from pydantic import BaseModel

from src import domain


class CreatedRoleResponseSchema(BaseModel):
    role_id: str
    role_name: str
    description: str
    security_level: int
    permissions: list[str]

    @classmethod
    def from_entity(cls, role: domain.Role) -> Self:
        return cls(
            role_id=role.id,
            role_name=role.name.to_raw(),
            description=role.description,
            security_level=role.security_level,
            permissions=[perm.permission_name.to_raw() for perm in role.permission],
        )


class RoleDeletedResponseSchema(BaseModel):
    status: str = "Given role successfully deleted"


class RoleAssignedResponseSchema(BaseModel):
    user_id: str
    username: str
    roles: list[str]

    @classmethod
    def from_entity(cls, user: domain.User) -> Self:
        return cls(
            user_id=user.id.to_raw(),
            username=user.username.to_raw(),
            roles=[role.name.to_raw() for role in user.roles],
        )


class GetRolesResponseSchema(BaseModel):
    roles: list[CreatedRoleResponseSchema]

    @classmethod
    def from_entity(cls, roles: list[domain.Role]) -> Self:
        return cls(
            roles=[CreatedRoleResponseSchema.from_entity(role) for role in roles]
        )


class RoleRemovedResponseSchema(RoleAssignedResponseSchema): ...


class RoleUpdatedResponseSchema(CreatedRoleResponseSchema): ...
