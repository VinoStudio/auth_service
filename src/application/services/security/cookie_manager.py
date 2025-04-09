from dataclasses import dataclass
from typing import Optional

from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol
from src.application.base.security.cookie_manager import BaseCookieManager


@dataclass
class CookieManager(BaseCookieManager):
    cookie_path: str
    cookie_secure: bool
    cookie_httponly: bool
    cookie_samesite: str
    cookie_max_age: int

    def set_cookie(
        self, response: ResponseProtocol, token: str, key: str = "refresh_token"
    ) -> None:
        response.set_cookie(
            key=key,
            value=token,
            max_age=self.cookie_max_age,
            path=self.cookie_path,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )

    def delete_cookie(self, response: ResponseProtocol, key: str) -> None:
        response.delete_cookie(
            key=key,
            path=self.cookie_path,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )

    def get_cookie(self, request: RequestProtocol, key: str) -> Optional[str]:
        return request.cookies.get(key)
