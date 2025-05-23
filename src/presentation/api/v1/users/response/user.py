from datetime import datetime
from typing import Self

from pydantic import BaseModel

from src import domain


class GetUserResponseSchema(BaseModel):
    user_id: str
    username: str
    roles: list[str]
    created_at: datetime
    is_deleted: bool

    @classmethod
    def from_entity(cls, user: domain.User) -> Self:
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
    def from_entity(cls, session: domain.Session) -> Self:
        return cls(
            user_id=session.user_id,
            user_agent=session.user_agent,
            device_id=session.device_id,
            last_activity=session.last_activity,
            is_active=session.is_active,
        )


class GetUserSessionsResponseSchema(BaseModel):
    sessions: list[GetUserSessionResponseSchema]

    @classmethod
    def from_entity(cls, sessions: list[domain.Session]) -> Self:
        return cls(
            sessions=[
                GetUserSessionResponseSchema.from_entity(session)
                for session in sessions
            ]
        )


class GetUserConnectedAccountResponseSchema(BaseModel):
    provider: str
    provider_user_id: str
    provider_email: str

    @classmethod
    def from_entity(cls, account: domain.OAuthAccount) -> Self:
        return cls(
            provider=account.provider,
            provider_user_id=account.provider_user_id,
            provider_email=account.provider_email,
        )


class GetUserConnectedAccountsResponseSchema(BaseModel):
    accounts: list[GetUserConnectedAccountResponseSchema]

    @classmethod
    def from_entity(cls, accounts: list[domain.OAuthAccount]) -> Self:
        return cls(
            accounts=[
                GetUserConnectedAccountResponseSchema.from_entity(account)
                for account in accounts
            ]
        )


class GetUserRolesResponseSchema(BaseModel):
    roles: list[str]


class GetUserPermissionsResponseSchema(BaseModel):
    permissions: list[str]
