from dataclasses import dataclass
from typing import Optional

from src.application.base.session.session_manager import BaseSessionManager
from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol
from src.application.base.security import BaseJWTManager
from src.application.dto.token import TokenPair
from src.application.base.commands import BaseCommand, CommandHandler
from src.application.exceptions import PasswordIsInvalidException
from src.application.services.security.security_user import SecurityUser
from src.infrastructure.base.repository import BaseUserReader
from src.infrastructure.base.uow import UnitOfWork

from src.domain.user.values import Password

import src.domain as domain
import src.application.dto as dto


@dataclass(frozen=True)
class LoginUserCommand(BaseCommand):
    email_or_username: str
    password: str
    request: Optional[RequestProtocol]
    response: Optional[ResponseProtocol]


@dataclass(frozen=True)
class LoginUserCommandHandler(CommandHandler[LoginUserCommand, TokenPair]):
    _user_reader: BaseUserReader
    _jwt_manager: BaseJWTManager
    _session_manager: BaseSessionManager
    _uow: UnitOfWork

    async def handle(self, command: LoginUserCommand) -> TokenPair:
        user_credentials: dto.UserCredentials = (
            await self._user_reader.get_user_credentials_by_email_or_username(
                command.email_or_username
            )
        )

        user_pass = Password(user_credentials.hashed_password)

        if not user_pass.verify(password=command.password):
            raise PasswordIsInvalidException(command.password)

        created_session: domain.Session = (
            await self._session_manager.get_or_create_session(
                user_id=user_credentials.user_id, request=command.request
            )
        )

        security_user = SecurityUser.create_from_jwt_data(
            jwt_data=user_credentials.jwt_data, device_id=created_session.device_id
        )

        return self._jwt_manager.create_token_pair(
            security_user=security_user, response=command.response
        )
