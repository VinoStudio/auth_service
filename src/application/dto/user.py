from src.application.base.dto.dto import DTO
from dataclasses import dataclass


@dataclass(frozen=True)
class UserCredentials(DTO):
    user_id: str
    jwt_data: bytes
    hashed_password: bytes


@dataclass(frozen=True)
class OauthUserCredentials(DTO):
    email: str
    username: str
    password: str
    first_name: str | None
    last_name: str | None
    middle_name: str | None
