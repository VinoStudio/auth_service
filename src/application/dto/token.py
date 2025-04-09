from src.application.base.dto.dto import DTO

from dataclasses import dataclass
from datetime import datetime
from typing import List

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
    roles: List[str]
    permissions: List[str]

