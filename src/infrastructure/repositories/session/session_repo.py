from typing import Optional, Dict, Any, List

from sqlalchemy import select, text

from src.infrastructure.base.repository import SQLAlchemyRepository
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC, timezone

from src.infrastructure.base.repository.session_repo import BaseSessionRepository
from src.infrastructure.db.models import UserSession

from uuid6 import uuid7


@dataclass
class SessionRepository(BaseSessionRepository, SQLAlchemyRepository):
    """Repository for managing refresh tokens in the database"""

    async def create_session(
        self, user_id: str, client_info: Dict[str, Any]
    ) -> UserSession:
        """Create a new user session record"""
        user_session = UserSession(
            id=str(uuid7()),
            user_agent=client_info.get("user_agent", "unknown"),
            device_info=client_info.get("device", "unknown"),
            is_active=True,
            user_id=user_id,
        )
        self._session.add(user_session)
        await self._session.refresh(user_session)
        return user_session

    async def get_active_sessions(self, user_id: str) -> List[UserSession]:
        """Get all active sessions for a user"""
        result = await self._session.execute(
            select(UserSession).filter(
                UserSession.user_id == user_id, UserSession.is_active == True
            )
        )
        return [*result.scalars().all()]

    async def deactivate_session(self, session_id: str) -> Optional[UserSession]:
        """Deactivate a user session"""
        result = await self._session.execute(
            select(UserSession).filter(UserSession.id == session_id)
        )
        session = result.scalars().first()

        if session:
            session.is_active = False
            await self._session.commit()
            await self._session.refresh(session)

        return session

    async def deactivate_all_sessions(self, user_id: str) -> int:
        """Deactivate all sessions for a user"""
        sessions = await self.get_active_sessions(user_id)
        count = 0

        for session in sessions:
            session.is_active = False
            count += 1

        await self._session.commit()
        return count

    async def update_session_activity(self, session_id: str) -> None:
        """Update the last activity time of a session"""
        await self._session.execute(
            text(
                """
                UPDATE user_session
                SET last_activity = :last_activity
                WHERE id = :session_id
                """
            ),
            dict(session_id=session_id, last_activity=datetime.now(UTC)),
        )
