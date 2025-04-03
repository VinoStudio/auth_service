from src.application.base.security.jwt_encoder import BaseJWTEncoder
from dataclasses import dataclass
from typing import Dict, Any
from jose import jwt


@dataclass(frozen=True)
class JWTEncoder(BaseJWTEncoder):
    secret_key: str
    algorithm: str

    def encode(self, payload: Dict[str, Any]) -> str:
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode(self, token: str) -> Dict[str, Any]:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
