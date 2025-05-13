from functools import lru_cache

from aiojobs import Scheduler
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide

from src.application.cqrs.cqrs_di_setup import MediatorConfigProvider, MediatorProvider
from src.application.cqrs.permission.permission_di_setup import (
    PermissionCommandProvider,
    PermissionQueryProvider,
)
from src.application.cqrs.role.role_di_setup import (
    RoleCommandProvider,
    RoleQueryProvider,
)
from src.application.cqrs.user.user_di_setup import (
    ExternalEventProvider,
    UserCommandProvider,
    UserQueryProvider,
)
from src.application.services.rbac.rbac_di_setup import RBACProvider
from src.application.services.security.jwt_di_setup import JWTProvider
from src.application.services.session.session_di_setup import SessionManagerProvider
from src.application.services.tasks.task_di_setup import NotificationManagerProvider
from src.infrastructure.db.database_di_setup import DatabaseProvider, SessionProvider
from src.infrastructure.message_broker.message_broker_di_setup import (
    KafkaConsumerManagerProvider,
    MessageBrokerProvider,
)
from src.infrastructure.repositories.repo_di_setup import (
    RepositoryProvider,
    UnitOfWorkProvider,
)
from src.settings.config import ConfigProvider


@lru_cache(maxsize=1)
def get_container() -> AsyncContainer:
    return make_async_container(
        ConfigProvider(),
        DatabaseProvider(),
        SessionProvider(),
        RepositoryProvider(),
        UnitOfWorkProvider(),
        MessageBrokerProvider(),
        JWTProvider(),
        RBACProvider(),
        SessionManagerProvider(),
        NotificationManagerProvider(),
        MediatorProvider(),
        UserCommandProvider(),
        UserQueryProvider(),
        RoleCommandProvider(),
        RoleQueryProvider(),
        PermissionCommandProvider(),
        PermissionQueryProvider(),
        ExternalEventProvider(),
        MediatorConfigProvider(),
        KafkaConsumerManagerProvider(),
        SchedulerProvider(),
    )


class SchedulerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_scheduler_provider(self) -> Scheduler:
        return Scheduler()
