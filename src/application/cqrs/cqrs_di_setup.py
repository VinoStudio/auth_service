from dishka import Scope, provide, Provider, decorate

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
    RegisterUserCommand,
    RegisterUserCommandHandler,
    RegisterOAuthUserCommand,
    RegisterOAuthUserCommandHandler,
    AddOAuthAccountRequestCommand,
    AddOAuthAccountRequestCommandHandler,
    AddOAuthAccountToCurrentUserCommand,
    AddOAuthAccountToCurrentUserCommandHandler,
    LoginUserCommand,
    LoginUserCommandHandler,
    OAuthLoginUserCommand,
    OAuthLoginUserCommandHandler,
    LogoutUserCommand,
    LogoutUserCommandHandler,
    RefreshUserTokensCommand,
    RefreshUserTokensCommandHandler,
    ResetPasswordRequestCommand,
    ResetPasswordRequestCommandHandler,
    ResetUserPasswordCommand,
    ResetUserPasswordCommandHandler,
    ChangeEmailRequestCommand,
    ChangeEmailRequestCommandHandler,
    ChangeUserEmailCommand,
    ChangeUserEmailCommandHandler,
)

from src.application.cqrs.role.commands import (
    CreateRoleCommand,
    CreateRoleCommandHandler,
    AssignRoleCommand,
    AssignRoleCommandHandler,
    DeleteRoleCommand,
    DeleteRoleCommandHandler,
    RemoveRoleCommand,
    RemoveRoleCommandHandler,
    UpdateRoleSecurityLvlCommand,
    UpdateRoleSecurityLvlCommandHandler,
    UpdateRoleDescriptionCommand,
    UpdateRoleDescriptionCommandHandler,
    UpdateRolePermissionsCommand,
    UpdateRolePermissionsCommandHandler,
    RemoveRolePermissionsCommand,
    RemoveRolePermissionsCommandHandler,
)

from src.application.cqrs.permission.commands import (
    CreatePermissionCommand,
    CreatePermissionCommandHandler,
    DeletePermissionCommand,
    DeletePermissionCommandHandler,
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

from src.application.cqrs.role.queries import (
    GetAllRolesQuery,
    GetAllRolesHandler,
)

from src.application.cqrs.permission.queries import (
    GetAllPermissionsQuery,
    GetAllPermissionsHandler,
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
    async def get_event_dispatcher(self) -> BaseEventDispatcher:
        return EventDispatcher()


class MediatorConfigProvider(Provider):
    @decorate
    async def register_user_commands(
        self,
        command_mediator: BaseCommandMediator,
        register_user: RegisterUserCommandHandler,
        register_oauth_user: RegisterOAuthUserCommandHandler,
        login_user: LoginUserCommandHandler,
        oauth_login: OAuthLoginUserCommandHandler,
        logout_user: LogoutUserCommandHandler,
        refresh_user_tokens: RefreshUserTokensCommandHandler,
        reset_user_password_request: ResetPasswordRequestCommandHandler,
        reset_user_password: ResetUserPasswordCommandHandler,
        change_email_request: ChangeEmailRequestCommandHandler,
        change_user_email: ChangeUserEmailCommandHandler,
        add_oauth_account: AddOAuthAccountToCurrentUserCommandHandler,
        add_oauth_account_request: AddOAuthAccountRequestCommandHandler,
    ) -> BaseCommandMediator:

        command_mediator.register_command(RegisterUserCommand, [register_user])
        command_mediator.register_command(
            RegisterOAuthUserCommand, [register_oauth_user]
        )
        command_mediator.register_command(
            AddOAuthAccountRequestCommand, [add_oauth_account_request]
        )
        command_mediator.register_command(
            AddOAuthAccountToCurrentUserCommand, [add_oauth_account]
        )
        command_mediator.register_command(LoginUserCommand, [login_user])
        command_mediator.register_command(OAuthLoginUserCommand, [oauth_login])
        command_mediator.register_command(LogoutUserCommand, [logout_user])
        command_mediator.register_command(
            RefreshUserTokensCommand, [refresh_user_tokens]
        )
        command_mediator.register_command(
            ResetPasswordRequestCommand, [reset_user_password_request]
        )
        command_mediator.register_command(
            ResetUserPasswordCommand, [reset_user_password]
        )
        command_mediator.register_command(
            ChangeEmailRequestCommand, [change_email_request]
        )
        command_mediator.register_command(ChangeUserEmailCommand, [change_user_email])

        return command_mediator

    @decorate
    async def register_role_commands(
        self,
        command_mediator: BaseCommandMediator,
        create_role: CreateRoleCommandHandler,
        assign_role: AssignRoleCommandHandler,
        delete_role: DeleteRoleCommandHandler,
        remove_role: RemoveRoleCommandHandler,
        update_role_security_lvl: UpdateRoleSecurityLvlCommandHandler,
        update_role_description: UpdateRoleDescriptionCommandHandler,
        update_role_permissions: UpdateRolePermissionsCommandHandler,
        remove_role_permissions: RemoveRolePermissionsCommandHandler,
    ) -> BaseCommandMediator:

        command_mediator.register_command(CreateRoleCommand, [create_role])
        command_mediator.register_command(AssignRoleCommand, [assign_role])
        command_mediator.register_command(DeleteRoleCommand, [delete_role])
        command_mediator.register_command(RemoveRoleCommand, [remove_role])
        command_mediator.register_command(
            UpdateRoleSecurityLvlCommand, [update_role_security_lvl]
        )
        command_mediator.register_command(
            UpdateRoleDescriptionCommand, [update_role_description]
        )
        command_mediator.register_command(
            UpdateRolePermissionsCommand, [update_role_permissions]
        )
        command_mediator.register_command(
            RemoveRolePermissionsCommand, [remove_role_permissions]
        )

        return command_mediator

    @decorate
    async def register_permission_commands(
        self,
        command_mediator: BaseCommandMediator,
        create_permission: CreatePermissionCommandHandler,
        delete_permission: DeletePermissionCommandHandler,
    ) -> BaseCommandMediator:
        command_mediator.register_command(CreatePermissionCommand, [create_permission])
        command_mediator.register_command(DeletePermissionCommand, [delete_permission])

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

    @decorate
    async def register_role_queries(
        self,
        query_mediator: BaseQueryMediator,
        get_roles: GetAllRolesHandler,
    ) -> BaseQueryMediator:

        query_mediator.register_query(GetAllRolesQuery, get_roles)

        return query_mediator

    @decorate
    async def register_permission_queries(
        self,
        query_mediator: BaseQueryMediator,
        get_permissions: GetAllPermissionsHandler,
    ) -> BaseQueryMediator:

        query_mediator.register_query(GetAllPermissionsQuery, get_permissions)

        return query_mediator
