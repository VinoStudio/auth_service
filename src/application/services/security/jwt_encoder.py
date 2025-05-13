from dataclasses import dataclass
from typing import Any

from jose import jwt

from src.application.base.security.jwt_encoder import BaseJWTEncoder


@dataclass(frozen=True)
class JWTEncoder(BaseJWTEncoder):
    """
    Handles JWT token encoding and decoding operations.

    Provides methods to encode payloads into JWT tokens and decode tokens
    back into their original payload. This implementation is immutable
    (frozen dataclass) to prevent modification of security-critical
    attributes after initialization.

    Attributes:
        secret_key: Secret key used for signing JWT tokens
        algorithm: The cryptographic algorithm used for signing (e.g., 'HS256')
    """

    secret_key: str
    algorithm: str

    def encode(self, payload: dict[str, Any]) -> str:
        """
        Encode a payload dictionary into a JWT token string.

        Signs the payload with the configured secret key and algorithm
        to produce a secure JWT token.

        Args:
            payload: Dictionary containing claims to encode into the JWT

        Returns:
            str: The encoded JWT token as a string
        """
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict[str, Any]:
        """
        Decode a JWT token string back into its payload dictionary.

        Verifies the token signature using the configured secret key
        and algorithm, then returns the decoded claims.

        Args:
            token: JWT token string to decode

        Returns:
            Dict[str, Any]: Dictionary containing the decoded JWT claims

        Raises:
            ExpiredSignatureError: If the token has expired
            JWTError: If the token is invalid or the signature verification fails
        """
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
