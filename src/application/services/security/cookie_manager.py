from dataclasses import dataclass
from typing import Optional

from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol
from src.application.base.security.cookie_manager import BaseCookieManager


@dataclass
class CookieManager(BaseCookieManager):
    """
    Manages HTTP cookies for authentication tokens.

    Handles cookie operations for storing, retrieving, and removing
    authentication tokens (primarily refresh tokens) in HTTP cookies.
    Implements secure cookie practices with configurable security settings.

    Attributes:
        cookie_path: URL path restriction for the cookie
        cookie_secure: Whether the cookie should only be sent over HTTPS
        cookie_httponly: Whether the cookie is inaccessible to JavaScript
        cookie_samesite: Cross-site request protection ('lax', 'strict', or 'none')
        cookie_max_age: Default maximum age of cookies in seconds
    """

    cookie_path: str
    cookie_secure: bool
    cookie_httponly: bool
    cookie_samesite: str
    cookie_max_age: int

    def set_cookie(
        self,
        response: ResponseProtocol,
        token: str,
        max_age: int = None,
        key: str = "refresh_token",
    ) -> None:
        """
        Set a cookie in the HTTP response.

        Creates or updates a cookie containing the specified token with
        the configured security settings.

        Args:
            response: The HTTP response object to which the cookie will be added
            token: The token value to store in the cookie
            max_age: Optional override for cookie expiration in seconds
                    (defaults to self.cookie_max_age if not specified)
            key: Cookie name (defaults to "refresh_token")
        """
        response.set_cookie(
            key=key,
            value=token,
            max_age=max_age or self.cookie_max_age,
            path=self.cookie_path,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )

    def delete_cookie(self, response: ResponseProtocol, key: str) -> None:
        """
        Delete a cookie from the HTTP response.

        Instructs the client to remove the specified cookie by setting
        its expiration to the past.

        Args:
            response: The HTTP response object from which to delete the cookie
            key: Cookie name to delete
        """
        response.delete_cookie(
            key=key,
            path=self.cookie_path,
        )

    def get_cookie(self, request: RequestProtocol, key: str) -> Optional[str]:
        """
        Retrieve a cookie value from the HTTP request.

        Extracts the specified cookie from the request if it exists.

        Args:
            request: The HTTP request object containing cookies
            key: Cookie name to retrieve

        Returns:
            Optional[str]: The cookie value if found, otherwise None
        """
        return request.cookies.get(key)
