from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol


@dataclass
class BaseCookieManager(ABC):
    """
    Protocol defining the interface for HTTP cookie management.

    Responsible for secure handling of cookies used for authentication
    tokens and session management.
    """

    @abstractmethod
    def set_cookie(
        self,
        response: ResponseProtocol,
        key: str,
        token: str,
        max_age: int | None = None,
    ) -> None:
        """
        Set a cookie in the HTTP response.

        Args:
            response: The HTTP response object to which the cookie will be added
            token: The token value to store in the cookie
            max_age: Optional override for cookie expiration in seconds
            key: Cookie name (defaults to "refresh_token")
        """
        raise NotImplementedError

    @abstractmethod
    def delete_cookie(self, response: ResponseProtocol, key: str) -> None:
        """
        Delete a cookie from the HTTP response.

        Args:
            response: The HTTP response object from which to delete the cookie
            key: Cookie name to delete
        """
        raise NotImplementedError

    @abstractmethod
    def get_cookie(self, request: RequestProtocol, key: str) -> str | None:
        """
        Retrieve a cookie value from the HTTP request.

        Args:
            request: The HTTP request object containing cookies
            key: Cookie name to retrieve

        Returns:
            Optional[str]: The cookie value if found, otherwise None
        """
        raise NotImplementedError
