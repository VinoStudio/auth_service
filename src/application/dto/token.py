from dataclasses import dataclass

from src.application.base.dto.dto import DTO


@dataclass(frozen=True)
class TokenPair(DTO):
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class Token(DTO):
    type: str
    sub: str
    lvl: int
    jti: str
    did: str
    exp: float
    iat: float
    roles: list[str]
    permissions: list[str]
