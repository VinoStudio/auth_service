from abc import ABC, abstractmethod
from typing import Any
from src.application.base.interface.request import RequestProtocol


class BaseSessionManager(ABC):
    @abstractmethod
    async def get_or_create_session(
        self, user_id: str, request: RequestProtocol
    ) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def deactivate_user_session(self, user_id: str, device_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def deactivate_session(self, session_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def deactivate_all_user_sessions(self, user_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_session_activity(self, session_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_user_active_sessions(self, user_id: str) -> Any:
        raise NotImplementedError
