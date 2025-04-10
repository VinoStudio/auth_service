from dishka import Scope, provide, Provider
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.application.cqrs.user.commands import (
    LoginUserCommandHandler,
    LogoutUserCommandHandler,
    RefreshUserTokensCommandHandler,
    RegisterUserCommandHandler,
)

from src.application.cqrs.user.events import UserCreatedEventHandler
from src.application.services.tasks.notification_manager import NotificationManager
from src.settings.config import Config


class UserCommandProvider(Provider):

    register_user = provide(RegisterUserCommandHandler, scope=Scope.REQUEST)
    login_user = provide(LoginUserCommandHandler, scope=Scope.REQUEST)
    logout_user = provide(LogoutUserCommandHandler, scope=Scope.REQUEST)
    refresh_user_tokens = provide(RefreshUserTokensCommandHandler, scope=Scope.APP)


# class UserEventProvider(Provider):
#     user_registered = provide(RegisterUserCommandHandler, scope=Scope.APP)


class ExternalEventProvider(Provider):
    @provide(scope=Scope.APP)
    async def user_created(
        self,
        session_factory: async_sessionmaker,
        notification_manager: NotificationManager,
    ) -> UserCreatedEventHandler:
        return UserCreatedEventHandler(session_factory, notification_manager)
