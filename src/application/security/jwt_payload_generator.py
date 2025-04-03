from src.application.base.security.jwt_payload import BaseJWTPayloadGenerator
from src.application.base.security.jwt_user import JWTUserInterface
from src.application.security.token_type import TokenType

from uuid6 import uuid7
from dataclasses import dataclass
from datetime import datetime, UTC, timedelta
from typing import Dict, Any


@dataclass(frozen=True)
class JWTPayloadGenerator(BaseJWTPayloadGenerator):
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    def generate(self, user: JWTUserInterface, token_type: TokenType) -> Dict[str, Any]:

        now = datetime.now(UTC)
        payload = {
            "type": token_type,
            "sub": user.get_user_identifier(),
            "did": user.get_device_id(),
            "roles": user.get_roles(),
            "permissions": user.get_permissions(),
            "jti": str(uuid7()),
            "exp": (
                now
                + timedelta(
                    minutes=(
                        self.access_token_expire_minutes
                        if token_type == TokenType.ACCESS.value
                        else self.refresh_token_expire_minutes
                    )
                )
            ).timestamp(),  # Returns float with microseconds
            "iat": now.timestamp(),  # Returns float with microseconds
        }

        return payload
