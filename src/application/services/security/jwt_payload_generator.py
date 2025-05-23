from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from uuid6 import uuid7

from src.application.base.security.jwt_payload import BaseJWTPayloadGenerator
from src.application.base.security.jwt_user import JWTUserInterface
from src.application.services.security.token_type import TokenType


@dataclass(frozen=True)
class JWTPayloadGenerator(BaseJWTPayloadGenerator):
    """
    Generates JWT payloads for authentication tokens.

    Creates standardized JWT payloads containing user identity, permissions,
    and time-based constraints for both access and refresh tokens.
    This implementation is immutable (frozen dataclass).

    Attributes:
        access_token_expire_minutes: Number of minutes until access tokens expire
        refresh_token_expire_minutes: Number of minutes until refresh tokens expire
    """

    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    def generate(self, user: JWTUserInterface, token_type: TokenType) -> dict[str, Any]:
        """
        Generate a JWT payload for the specified user and token type.

        Creates a dictionary containing all required JWT claims including:
        - Token type (access or refresh)
        - Subject identifier (user ID)
        - Security level
        - Device identifier
        - User roles and permissions
        - Unique token identifier (jti)
        - Expiration time (based on token type)
        - Issued-at timestamp

        Args:
            user: User object containing authentication information
            token_type: Type of token to generate (ACCESS or REFRESH)

        Returns:
            Dict[str, Any]: JWT payload dictionary with all required claims

        Note:
            Expiration time is calculated based on the token type, with
            access tokens having a shorter lifetime than refresh tokens.
            All timestamps are in UTC.
        """
        now = datetime.now(UTC)
        payload = {
            "type": token_type,
            "sub": user.get_user_identifier(),
            "lvl": user.get_security_level(),
            "did": user.get_device_id(),
            "roles": user.get_roles(),
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

        if token_type == TokenType.ACCESS.value:
            payload["permissions"] = user.get_permissions()

        return payload
