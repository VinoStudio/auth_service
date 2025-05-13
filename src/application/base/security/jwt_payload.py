from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from src.application.base.security import JWTUserInterface


@dataclass(frozen=True)
class BaseJWTPayloadGenerator(ABC):
    """
    Protocol defining the interface for JWT payload generation.

    Responsible for creating standardized JWT payloads that contain
    authentication and authorization information.
    """

    @abstractmethod
    def generate(self, user: JWTUserInterface, token_type: Any) -> dict[str, Any]:
        """
        Generate a JWT payload for the specified user and token type.

        Args:
            user: User object containing authentication information
            token_type: Type of token to generate (typically ACCESS or REFRESH)

        Returns:
            Dict[str, Any]: JWT payload dictionary with all required claims
        """
        raise NotImplementedError
