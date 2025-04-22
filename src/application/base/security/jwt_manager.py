from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Dict, TYPE_CHECKING

from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol

import src.application.dto as dto

if TYPE_CHECKING:
    from src.application.base.security.jwt_user import JWTUserInterface


@dataclass
class BaseJWTManager:
    """
    Manages JWT authentication tokens including creation, validation, and revocation.

    This class handles token creation, refresh operations, cookie management,
    and maintains a token blacklist for revoked access.

    """

    @abstractmethod
    def create_token_pair(
        self,
        security_user: "JWTUserInterface",
    ) -> dto.TokenPair:
        """
        Create a new pair of access and refresh tokens for a user.

        Generates both access and refresh tokens with appropriate payloads
        for the given user.

        Args:
            security_user: User object containing authentication information
                id: str
                roles: List[str]
                permissions: List[str]
                security_level: int | None
                device_id: str | None

        Returns:
            dto.TokenPair: Object containing both access_token and refresh_token
        """

        raise NotImplementedError

    @abstractmethod
    def get_token_from_cookie(self, request: RequestProtocol) -> str:
        """
        Extract and return the refresh token from the request's cookie.

        Args:
            request: The HTTP request object from witch the cookie will be extracted

        Returns:
            str: The refresh token extracted from cookies

        Raises:
            AccessRejectedException: If the refresh token is missing from cookies
        """
        raise NotImplementedError

    @abstractmethod
    def set_token_in_cookie(self, response: ResponseProtocol, token: str) -> None:
        """
        Set the refresh token in the response's cookies.

        Args:
            response: The HTTP response object to which the cookie will be added
            token: The refresh token to store in the cookie
        """

        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_access_token_from_request(request) -> str:
        """
        Extract and return the access token from the request's Authorization header.

        Validates that the Authorization header exists and is properly formatted as
        a Bearer token.

        Args:
            request: The HTTP request object from witch the access token will be extracted

        Returns:
            str: The access token from the Authorization header

        Raises:
            AccessRejectedException: If the token is missing, empty, or incorrectly formatted
        """

        raise NotImplementedError

    @abstractmethod
    async def validate_token(self, token: str) -> dto.Token:
        """
        Validate a JWT token and check if it has been revoked.

        Decodes the token and verifies it hasn't been blacklisted due to user logout,
        deletion, or role invalidation. Checks both user-specific blacklisting and
        role-based invalidation.

        Args:
            token: The JWT token string to validate

        Returns:
            dto.Token: Object containing the decoded token data
                type: str
                sub: str
                lvl: int
                jti: str
                did: str
                exp: float
                iat: float
                roles: List[str]
                permissions: List[str]

        Raises:
            TokenRevokedException: If the token has been revoked (user in blacklist or role invalidated)
            TokenExpiredException: If the token has expired
            TokenValidationError: If the token cannot be decoded or is invalid
        """

        raise NotImplementedError

    @abstractmethod
    async def refresh_tokens(
        self, request: RequestProtocol, response: ResponseProtocol
    ) -> dto.TokenPair:
        """
        Refresh a user's authentication by issuing new token pair.

        Validates the current refresh token from cookies, then generates and returns
        a new token pair. Sets the new refresh token in cookies.

        Args:
            request: The HTTP request object containing the current refresh token
            response: The HTTP response object for setting the new refresh token

        Returns:
            dto.TokenPair: Object containing new access_token and refresh_token

        Raises:
            ValueError: If the refresh process fails (invalid session, missing data)
            TokenRevokedException: If the current token has been revoked
            TokenExpiredException: If the current token has expired
            TokenValidationError: If the current token is invalid
            AccessRejectedException: If the refresh token is missing from cookies
        """

        raise NotImplementedError

    @abstractmethod
    async def revoke_token(self, response: ResponseProtocol, token: str) -> None:
        """
        Revoke a user's authentication token.

        Clears the refresh token cookie and adds the user ID to the blacklist.
        The blacklist entry includes a buffer period beyond the token's expiration
        to ensure security.

        Args:
            response: The HTTP response object for clearing the refresh token cookie
            token: The JWT token to revoke

        Raises:
            JWTError: If the token cannot be decoded
        """

        raise NotImplementedError
