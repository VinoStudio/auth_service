from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any

from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol


@dataclass
class BaseCookieManager(ABC):
    @abstractmethod
    def set_cookie(self, response: ResponseProtocol, key: str, token: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_cookie(self, response: ResponseProtocol, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_cookie(self, request: RequestProtocol, key: str) -> str | None:
        raise NotImplementedError
