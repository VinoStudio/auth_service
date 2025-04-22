from typing import Optional, Dict, Any, List, Sequence
from sqlalchemy import select, text
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC, timezone

from src.infrastructure.base.repository import SQLAlchemyRepository
from src.infrastructure.base.repository.session_repo import BaseSessionRepository
from src.infrastructure.repositories.converters import (
    OrmToDomainConverter,
    DomainToOrmConverter,
)

import src.infrastructure.db.models as models
import src.domain as domain


@dataclass
class SessionRepository(BaseSessionRepository, SQLAlchemyRepository):
    """Repository for managing refresh tokens in the database"""

    async def create_session(self, session: domain.Session) -> None:
        """Create a new user session record"""

        user_session: models.UserSession = DomainToOrmConverter.domain_to_user_session(
            session
        )

        self._session.add(user_session)
        await self._session.flush()

    async def get_session_by_id(self, session_id: str) -> Optional[domain.Session]:
        result = await self._session.execute(
            select(models.UserSession).where(models.UserSession.id == session_id)
        )

        user_session: models.UserSession = result.scalars().first()

        if not user_session:
            return None

        return OrmToDomainConverter.user_session_to_domain(user_session)

    async def get_active_session_by_device_id(
        self, user_id: str, device_id: str
    ) -> Optional[domain.Session]:
        """Find existing session by user ID and device ID"""

        result = await self._session.execute(
            select(models.UserSession).where(
                models.UserSession.user_id == user_id,
                models.UserSession.device_id == device_id,
            )
        )

        user_session: models.UserSession = result.scalars().first()

        if not user_session:
            return None

        return OrmToDomainConverter.user_session_to_domain(user_session)

    async def get_user_active_sessions(self, user_id: str) -> List[domain.Session]:
        """Get all active sessions for a user"""
        result = await self._session.execute(
            select(models.UserSession).where(
                models.UserSession.user_id == user_id,
                models.UserSession.is_active == True,
            )
        )
        return [
            OrmToDomainConverter.user_session_to_domain(user_session)
            for user_session in result.scalars().all()
        ]

    async def deactivate_session(self, session_id: str) -> Optional[domain.Session]:
        """Deactivate a user session"""

        await self._session.execute(
            text(
                """
                UPDATE usersession
                SET is_active = :is_active
                WHERE id = :session_id
                """
            ),
            dict(is_active=False, session_id=session_id),
        )

    async def deactivate_user_session(self, user_id: str, device_id: str):
        await self._session.execute(
            text(
                """
                UPDATE usersession
                SET is_active = :is_active
                WHERE user_id = :user_id AND device_id = :device_id
                """
            ),
            dict(is_active=False, user_id=user_id, device_id=device_id),
        )

    async def get_user_sessions(self, user_id: str) -> Sequence[models.UserSession]:
        result = await self._session.execute(
            select(models.UserSession).filter(
                models.UserSession.user_id == user_id,
                models.UserSession.is_active == True,
            )
        )
        return result.scalars().all()

    async def deactivate_all_sessions(self, user_id: str) -> int:
        """Deactivate all sessions for a user"""
        sessions = await self.get_user_sessions(user_id)
        deactivated_count = 0

        for session in sessions:
            user_session: models.UserSession = session
            user_session.is_active = False
            await self._session.refresh(user_session)
            deactivated_count += 1

        return deactivated_count

    async def update_session_activity(self, session_id: str) -> None:
        """Update the last activity time of a session"""
        await self._session.execute(
            text(
                """
                UPDATE usersession
                SET last_activity = :last_activity
                WHERE id = :session_id
                """
            ),
            dict(session_id=session_id, last_activity=datetime.now(UTC)),
        )
