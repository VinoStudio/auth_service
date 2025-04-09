from dishka import Scope, provide, Provider
from src.application.base.session.session_manager import BaseSessionManager
from src.application.services.session.session_manager import SessionManager
from src.application.services.session.device_identifier import DeviceIdentifier
from src.infrastructure.base.repository import BaseSessionRepository


class SessionManagerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_device_identifier(self) -> DeviceIdentifier:
        return DeviceIdentifier()

    @provide(scope=Scope.REQUEST)
    async def get_session_manager(
        self,
        session_repo: BaseSessionRepository,
        device_identifier: DeviceIdentifier,
    ) -> BaseSessionManager:
        return SessionManager(
            session_repo=session_repo, device_identifier=device_identifier
        )
