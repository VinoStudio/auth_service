from dishka import Scope, provide, Provider, decorate
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.application.base.event_publisher.event_dispatcher import BaseEventDispatcher
from src.application.base.event_publisher.event_publisher import BaseEventPublisher
from src.application.base.mediator.command import BaseCommandMediator
from src.application.base.mediator.query import BaseQueryMediator
from src.application.event_handlers.event_dispatcher import EventDispatcher
from src.application.event_handlers.event_publisher import EventPublisher
from src.application.mediator.command_mediator import CommandMediator
from src.application.mediator.query_mediator import QueryMediator
from src.infrastructure.base.message_broker.producer import AsyncMessageProducer

from src.application.user.commands import (
    LoginUserCommand,
    RegisterUserCommand,
    RefreshUserTokensCommand,
    LogoutUserCommand,
    LoginUserCommandHandler,
    RegisterUserCommandHandler,
    RefreshUserTokensCommandHandler,
    LogoutUserCommandHandler,
)
from src.infrastructure.message_broker.events import UserRegistered
from src.application.user.events.internal.user_registered import (
    UserRegisteredEventHandler,
)


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
        return EventDispatcher(session_factory=session_factory)


class MediatorConfigProvider(Provider):
    @decorate
    async def register_commands(
        self,
        command_mediator: BaseCommandMediator,
        register_user: RegisterUserCommandHandler,
        login_user: LoginUserCommandHandler,
        logout_user: LogoutUserCommandHandler,
        refresh_user_tokens: RefreshUserTokensCommandHandler,
    ) -> BaseCommandMediator:
        command_mediator.register_command(RegisterUserCommand, [register_user])
        command_mediator.register_command(LoginUserCommand, [login_user])
        command_mediator.register_command(LogoutUserCommand, [logout_user])
        command_mediator.register_command(
            RefreshUserTokensCommand, [refresh_user_tokens]
        )

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
