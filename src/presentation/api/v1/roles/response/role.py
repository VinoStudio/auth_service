from pydantic import BaseModel
from typing import List
import src.domain as domain


class CreatedRoleResponseSchema(BaseModel):
    role_id: str
    role_name: str
    description: str
    security_level: int
    permissions: List[str]

    @classmethod
    def from_entity(cls, role: domain.Role):
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
    roles: List[str]

    @classmethod
    def from_entity(cls, user: domain.User):
        return cls(
            user_id=user.id.to_raw(),
            username=user.username.to_raw(),
            roles=[role.name.to_raw() for role in user.roles],
        )


class RoleRemovedResponseSchema(RoleAssignedResponseSchema): ...


class RoleUpdatedResponseSchema(CreatedRoleResponseSchema): ...
