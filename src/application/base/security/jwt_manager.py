from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Dict

from src.application.base.dto.dto import DTO
from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol


@dataclass
class BaseJWTManager(ABC):
    @abstractmethod
    def create_token_pair(self, security_user: Any, response: ResponseProtocol) -> Any:
        raise NotImplementedError

    @abstractmethod
    def validate_token(self, token: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_token_from_cookie(self, request: RequestProtocol) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def refresh_tokens(
        self, response: ResponseProtocol, request: RequestProtocol
    ) -> Any:
        raise NotImplementedError

    async def revoke_token(self, response: ResponseProtocol, token: str) -> Any:
        raise NotImplementedError
