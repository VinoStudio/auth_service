from datetime import datetime
from typing import List

from pydantic import BaseModel
import src.domain as domain


class GetUserResponseSchema(BaseModel):
    user_id: str
    username: str
    created_at: datetime
    is_deleted: bool

    @classmethod
    def from_entity(cls, user: domain.User):
        return cls(
            user_id=user.id.to_raw(),
            username=user.username.to_raw(),
            created_at=user.created_at,
            is_deleted=user.deleted_at is not None,
        )


class GetUserRolesResponseSchema(BaseModel):
    roles: List[str]


class GetUserPermissionsResponseSchema(BaseModel):
    permissions: List[str]
