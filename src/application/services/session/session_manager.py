from dataclasses import dataclass

from src import domain
from src.application import dto
from src.application.base.interface.request import RequestProtocol
from src.application.base.session.session_manager import BaseSessionManager
from src.application.services.session.device_identifier import DeviceIdentifier
from src.domain.session.values.device_info import DeviceInfo
from src.infrastructure.base.repository.session_repo import BaseSessionRepository


@dataclass
class SessionManager(BaseSessionManager):
    """
    Implementation of BaseSessionManager

    This class handles session lifecycle including creation, retrieval, updates,
    and deactivation. It tracks user activity across multiple devices and provides
    methods to manage session state.

    Attributes:
        session_repo: Repository for persistent storage of session data
        device_identifier: Service to generate and identify unique devices
    """

    session_repo: BaseSessionRepository
    device_identifier: DeviceIdentifier

    async def get_or_create_session(
        self, user_id: str, request: RequestProtocol
    ) -> domain.Session | None:
        # Generate device identification
        device_data: dto.DeviceInformation = (
            self.device_identifier.generate_device_info(request)
        )

        # Try to find existing session for this user+device
        if existing_session := await self.get_user_session(
            user_id=user_id, device_id=device_data.device_id
        ):
            return existing_session

        # No existing session found
        session = domain.Session(
            user_id=user_id,
            device_id=device_data.device_id,
            device_info=DeviceInfo.create(device_info=device_data.device_info),
            user_agent=device_data.user_agent,
        )

        await self.session_repo.create_session(session=session)

        return session

    async def get_user_session(
        self, user_id: str, device_id: str
    ) -> domain.Session | None:
        # Try to find existing session for this user+device
        active_session = await self.session_repo.get_active_session_by_device_id(
            user_id=user_id,
            device_id=device_id,
        )

        if active_session:
            # Update last activity and return existing session
            await self.update_session_activity(session_id=active_session.id)
            return active_session

        return active_session

    async def deactivate_user_session(self, user_id: str, device_id: str) -> None:
        await self.session_repo.deactivate_user_session(
            user_id=user_id, device_id=device_id
        )

    async def deactivate_session(self, session_id: str) -> None:
        await self.session_repo.deactivate_session(session_id=session_id)

    async def deactivate_all_user_sessions(self, user_id: str) -> None:
        await self.session_repo.deactivate_all_sessions(user_id=user_id)

    async def update_session_activity(self, session_id: str) -> None:
        await self.session_repo.update_session_activity(session_id=session_id)

    async def get_user_active_sessions(self, user_id: str) -> list[domain.Session]:
        return await self.session_repo.get_user_active_sessions(user_id=user_id)
