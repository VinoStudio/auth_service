from dishka import Scope, provide, Provider, decorate
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.application.base.event_publisher.event_dispatcher import BaseEventDispatcher
from src.application.base.event_publisher.event_publisher import BaseEventPublisher
from src.application.base.mediator.command import BaseCommandMediator
from src.application.base.mediator.query import BaseQueryMediator
from src.application.cqrs.user.events import UserCreatedEventHandler
from src.application.event_handlers.event_dispatcher import EventDispatcher
from src.application.event_handlers.event_publisher import EventPublisher
from src.application.mediator.command_mediator import CommandMediator
from src.application.mediator.query_mediator import QueryMediator
from src.infrastructure.base.message_broker.producer import AsyncMessageProducer

from src.application.cqrs.user.commands import (
    LoginUserCommand,
    RegisterUserCommand,
    RefreshUserTokensCommand,
    LogoutUserCommand,
    LoginUserCommandHandler,
    RegisterUserCommandHandler,
    RefreshUserTokensCommandHandler,
    LogoutUserCommandHandler,
)

from src.application.cqrs.role.commands import (
    CreateRoleCommandHandler,
    CreateRoleCommand,
)

from src.application.cqrs.user.queries import (
    GetUserById,
    GetUserByIdHandler,
    GetUserByUsername,
    GetUserByUsernameHandler,
    GetCurrentUser,
    GetCurrentUserHandler,
    GetCurrentUserRoles,
    GetCurrentUserRolesHandler,
    GetCurrentUserPermissions,
    GetCurrentUserPermissionsHandler,
    GetUserRoles,
    GetUserRolesHandler,
    GetUserPermissions,
    GetUserPermissionsHandler,
    GetUsers,
    GetUsersHandler,
)

from src.infrastructure.message_broker.events import UserRegistered
from src.application.cqrs.user.events.internal.user_registered import (
    UserRegisteredEventHandler,
)
from src.infrastructure.message_broker.events.external.user_created import UserCreated


class MediatorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_command_mediator(self) -> BaseCommandMediator:
        return CommandMediator()

    @provide(scope=Scope.REQUEST)
    async def get_query_mediator(self) -> BaseQueryMediator:
        return QueryMediator()

    @provide(scope=Scope.APP)
    async def get_event_publisher(
        self, message_broker: AsyncMessageProducer
    ) -> BaseEventPublisher:
        return EventPublisher(_message_broker=message_broker)

    @provide(scope=Scope.APP)
    async def get_event_dispatcher(
        self, session_factory: async_sessionmaker
    ) -> BaseEventDispatcher:
        return EventDispatcher()


class MediatorConfigProvider(Provider):
    @decorate
    async def register_user_commands(
        self,
        command_mediator: BaseCommandMediator,
        register_user: RegisterUserCommandHandler,
        login_user: LoginUserCommandHandler,
        logout_user: LogoutUserCommandHandler,
        refresh_user_tokens: RefreshUserTokensCommandHandler,
        create_role: CreateRoleCommandHandler,
    ) -> BaseCommandMediator:

        command_mediator.register_command(RegisterUserCommand, [register_user])
        command_mediator.register_command(LoginUserCommand, [login_user])
        command_mediator.register_command(LogoutUserCommand, [logout_user])
        command_mediator.register_command(
            RefreshUserTokensCommand, [refresh_user_tokens]
        )
        command_mediator.register_command(CreateRoleCommand, [create_role])

        return command_mediator

    @decorate
    async def register_events(
        self,
        event_publisher: BaseEventPublisher,
    ) -> BaseEventPublisher:
        event_publisher.register_event(
            event=UserRegistered, event_handlers=[UserRegisteredEventHandler()]
        )

        return event_publisher

    @decorate
    async def register_external_events(
        self,
        event_dispatcher: BaseEventDispatcher,
        user_created: UserCreatedEventHandler,
    ) -> BaseEventDispatcher:

        event_dispatcher.register_handler(UserCreated, [user_created])

        return event_dispatcher

    @decorate
    async def register_user_queries(
        self,
        query_mediator: BaseQueryMediator,
        get_user_by_id: GetUserByIdHandler,
        get_user_by_username: GetUserByUsernameHandler,
        get_current_user: GetCurrentUserHandler,
        get_current_user_roles: GetCurrentUserRolesHandler,
        get_current_user_permissions: GetCurrentUserPermissionsHandler,
        get_user_roles: GetUserRolesHandler,
        get_user_permissions: GetUserPermissionsHandler,
        get_users: GetUsersHandler,
    ) -> BaseQueryMediator:

        query_mediator.register_query(GetUserById, get_user_by_id)
        query_mediator.register_query(GetUserByUsername, get_user_by_username)
        query_mediator.register_query(GetCurrentUser, get_current_user)
        query_mediator.register_query(GetCurrentUserRoles, get_current_user_roles)
        query_mediator.register_query(
            GetCurrentUserPermissions, get_current_user_permissions
        )
        query_mediator.register_query(GetUserRoles, get_user_roles)
        query_mediator.register_query(GetUserPermissions, get_user_permissions)
        query_mediator.register_query(GetUsers, get_users)

        return query_mediator
