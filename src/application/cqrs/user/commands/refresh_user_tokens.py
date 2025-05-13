from dataclasses import dataclass

from src.application import dto
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol
from src.application.base.security import BaseJWTManager


@dataclass(frozen=True)
class RefreshUserTokensCommand(BaseCommand):
    request: RequestProtocol
    response: ResponseProtocol


@dataclass(frozen=True)
class RefreshUserTokensCommandHandler(
    CommandHandler[RefreshUserTokensCommand, dto.TokenPair]
):
    _jwt_manager: BaseJWTManager

    async def handle(self, command: RefreshUserTokensCommand) -> dto.TokenPair:
        return await self._jwt_manager.refresh_tokens(
            request=command.request, response=command.response
        )
