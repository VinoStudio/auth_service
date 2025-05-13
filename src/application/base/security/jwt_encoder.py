from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BaseJWTEncoder(ABC):
    """
    Protocol defining the interface for JWT token encoding and decoding.

    Responsible for securely converting between payload dictionaries and
    signed JWT token strings.
    """

    @abstractmethod
    def encode(self, payload: dict[str, Any]) -> str:
        """
        Encode a payload dictionary into a JWT token string.

        Args:
            payload: Dictionary containing claims to encode into the JWT

        Returns:
            str: The encoded JWT token as a string
        """
        raise NotImplementedError

    @abstractmethod
    def decode(self, token: str) -> dict[str, Any]:
        """
        Decode a JWT token string back into its payload dictionary.

        Args:
            token: JWT token string to decode

        Returns:
            Dict[str, Any]: Dictionary containing the decoded JWT claims

        Raises:
            ExpiredSignatureError: If the token has expired
            JWTError: If the token is invalid or the signature verification fails
        """
        raise NotImplementedError
