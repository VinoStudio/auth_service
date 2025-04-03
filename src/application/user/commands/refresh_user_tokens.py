from dataclasses import dataclass

from src.application.base.event_publisher.event_publisher import BaseEventPublisher
from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol
from src.application.base.security import BaseJWTManager
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.security.security_user import SecurityUser
from src.application.session.session_manager import SessionManager
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.db.uow import SQLAlchemyUoW

import src.application.dto as dto


@dataclass(frozen=True)
class RefreshUserTokensCommand(BaseCommand):
    request: RequestProtocol
    response: ResponseProtocol


@dataclass(frozen=True)
class RefreshUserTokensCommandHandler(CommandHandler[RefreshUserTokensCommand, None]):
    _jwt_manager: BaseJWTManager

    async def handle(self, command: RefreshUserTokensCommand) -> None:

        await self._jwt_manager.refresh_tokens(
            request=command.request, response=command.response
        )
