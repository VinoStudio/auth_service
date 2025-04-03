from dataclasses import dataclass

from src.application.base.event_publisher.event_publisher import BaseEventPublisher
from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol
from src.application.base.security import BaseJWTManager
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.session.session_manager import BaseSessionManager
from src.application.security.security_user import SecurityUser
from src.application.session.session_manager import SessionManager
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.db.uow import SQLAlchemyUoW

import src.application.dto as dto


@dataclass(frozen=True)
class LogoutUserCommand(BaseCommand):
    response: ResponseProtocol
    request: RequestProtocol


@dataclass(frozen=True)
class LogoutUserCommandHandler(CommandHandler[LogoutUserCommand, None]):
    _jwt_manager: BaseJWTManager
    _session_manager: BaseSessionManager
    _uow: UnitOfWork

    async def handle(self, command: LogoutUserCommand) -> None:

        refresh_token: str = await self._jwt_manager.get_token_from_cookie(
            command.request
        )

        token_data: dto.Token = await self._jwt_manager.validate_token(refresh_token)

        security_user: SecurityUser = SecurityUser.create_from_token_dto(token_data)

        await self._jwt_manager.revoke_token(command.response, refresh_token)

        await self._session_manager.deactivate_user_session(
            user_id=security_user.get_user_identifier(),
            device_id=security_user.get_device_id(),
        )
