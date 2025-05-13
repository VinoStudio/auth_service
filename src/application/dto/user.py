from dataclasses import dataclass

from src.application.base.dto.dto import DTO


@dataclass(frozen=True)
class UserCredentials(DTO):
    user_id: str
    username: str
    jwt_data: bytes
    hashed_password: bytes


@dataclass(frozen=True)
class OauthUserCredentials(DTO):
    provider_email: str
    username: str
    password: str
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    provider_name: str
    provider_user_id: str


@dataclass
class OAuthUserIdentity(DTO):
    user_id: str
    jwt_data: bytes
    provider_name: str
    provider_user_id: str
