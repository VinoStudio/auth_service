from datetime import datetime
from typing import List

from pydantic import BaseModel
import src.domain as domain


class GetUserResponseSchema(BaseModel):
    user_id: str
    username: str
    roles: List[str]
    created_at: datetime
    is_deleted: bool

    @classmethod
    def from_entity(cls, user: domain.User):
        return cls(
            user_id=user.id.to_raw(),
            username=user.username.to_raw(),
            roles=[role.name.to_raw() for role in user.roles],
            created_at=user.created_at,
            is_deleted=user.deleted_at is not None,
        )


class GetUserSessionResponseSchema(BaseModel):
    user_id: str
    user_agent: str
    device_id: str
    last_activity: datetime
    is_active: bool

    @classmethod
    def from_entity(cls, session: domain.Session):
        return cls(
            user_id=session.user_id,
            user_agent=session.user_agent,
            device_id=session.device_id,
            last_activity=session.last_activity,
            is_active=session.is_active,
        )


class GetUserSessionsResponseSchema(BaseModel):
    sessions: List[GetUserSessionResponseSchema]

    @classmethod
    def from_entity(cls, sessions: List[domain.Session]):
        return cls(
            sessions=[
                GetUserSessionResponseSchema.from_entity(session)
                for session in sessions
            ]
        )


class GetUserRolesResponseSchema(BaseModel):
    roles: List[str]


class GetUserPermissionsResponseSchema(BaseModel):
    permissions: List[str]
