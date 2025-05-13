from abc import ABC, abstractmethod

from src import domain
from src.infrastructure.db import models


class BaseSessionRepository(ABC):
    @abstractmethod
    async def create_session(self, session: domain.Session) -> None:
        """Create a new user session record"""
        raise NotImplementedError

    @abstractmethod
    async def get_session_by_id(self, session_id: str) -> domain.Session | None:
        """Find existing session by ID"""
        raise NotImplementedError

    @abstractmethod
    async def get_active_session_by_device_id(
        self, user_id: str, device_id: str
    ) -> domain.Session | None:
        """Find existing session by user ID and device ID"""
        raise NotImplementedError

    @abstractmethod
    async def get_user_active_sessions(self, user_id: str) -> list[domain.Session]:
        """Get all active sessions for a user"""
        raise NotImplementedError

    @abstractmethod
    async def deactivate_session(self, session_id: str) -> None:
        """Deactivate a user session"""
        raise NotImplementedError

    @abstractmethod
    async def deactivate_user_session(self, user_id: str, device_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_user_sessions(self, user_id: str) -> list[models.UserSession]:
        raise NotImplementedError

    @abstractmethod
    async def deactivate_all_sessions(self, user_id: str) -> int:
        """Deactivate all sessions for a user"""
        raise NotImplementedError

    @abstractmethod
    async def update_session_activity(self, session_id: str) -> None:
        """Update the last activity time of a session"""
        raise NotImplementedError
