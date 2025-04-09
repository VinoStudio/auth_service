from dishka import Scope, provide, Provider

from src.application.cqrs.user.commands import (
    LoginUserCommandHandler,
    LogoutUserCommandHandler,
    RefreshUserTokensCommandHandler,
    RegisterUserCommandHandler,
)
from src.settings.config import Config


class UserCommandProvider(Provider):

    register_user = provide(RegisterUserCommandHandler, scope=Scope.REQUEST)
    login_user = provide(LoginUserCommandHandler, scope=Scope.REQUEST)
    logout_user = provide(LogoutUserCommandHandler, scope=Scope.REQUEST)
    refresh_user_tokens = provide(RefreshUserTokensCommandHandler, scope=Scope.APP)


# class UserEventProvider(Provider):
#     user_registered = provide(RegisterUserCommandHandler, scope=Scope.APP)
