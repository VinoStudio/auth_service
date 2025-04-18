from dishka import Scope, provide, Provider
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.application.cqrs.user.commands import (
    LoginUserCommandHandler,
    OAuthLoginUserCommandHandler,
    LogoutUserCommandHandler,
    RefreshUserTokensCommandHandler,
    ResetPasswordRequestCommandHandler,
    RegisterUserCommandHandler,
    RegisterOAuthUserCommandHandler,
    ResetUserPasswordCommandHandler,
)

from src.application.cqrs.user.queries import (
    GetUserByUsernameHandler,
    GetCurrentUserHandler,
    GetUsersHandler,
    GetCurrentUserPermissionsHandler,
    GetCurrentUserRolesHandler,
    GetUserByIdHandler,
    GetUserRolesHandler,
    GetUserPermissionsHandler,
)

from src.application.cqrs.user.events import UserCreatedEventHandler
from src.application.services.tasks.notification_manager import NotificationManager
from src.settings.config import Config


class UserCommandProvider(Provider):

    register_user = provide(RegisterUserCommandHandler, scope=Scope.REQUEST)
    register_oauth_user = provide(RegisterOAuthUserCommandHandler, scope=Scope.REQUEST)
    login_user = provide(LoginUserCommandHandler, scope=Scope.REQUEST)
    oauth_login = provide(OAuthLoginUserCommandHandler, scope=Scope.REQUEST)
    logout_user = provide(LogoutUserCommandHandler, scope=Scope.REQUEST)
    refresh_user_tokens = provide(RefreshUserTokensCommandHandler, scope=Scope.APP)
    reset_user_password_request = provide(
        ResetPasswordRequestCommandHandler, scope=Scope.REQUEST
    )
    reset_user_password = provide(ResetUserPasswordCommandHandler, scope=Scope.REQUEST)


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


class UserQueryProvider(Provider):
    # Query handlers
    get_user_by_id = provide(GetUserByIdHandler, scope=Scope.REQUEST)
    get_user_by_username = provide(GetUserByUsernameHandler, scope=Scope.REQUEST)
    get_user_roles = provide(GetUserRolesHandler, scope=Scope.REQUEST)
    get_user_permissions = provide(GetUserPermissionsHandler, scope=Scope.REQUEST)
    get_current_user = provide(GetCurrentUserHandler, scope=Scope.REQUEST)
    get_current_user_roles = provide(GetCurrentUserRolesHandler, scope=Scope.REQUEST)
    get_current_user_permissions = provide(
        GetCurrentUserPermissionsHandler, scope=Scope.REQUEST
    )
    get_users = provide(GetUsersHandler, scope=Scope.REQUEST)
