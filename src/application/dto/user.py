from src.application.base.dto.dto import DTO
from dataclasses import dataclass


@dataclass(frozen=True)
class UserCredentials(DTO):
    user_id: str
    jwt_data: bytes
    hashed_password: bytes