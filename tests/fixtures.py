from dishka import AsyncContainer, make_async_container

from src.application.cqrs.cqrs_di_setup import MediatorConfigProvider, MediatorProvider
from src.application.cqrs.role.role_di_setup import RoleCommandProvider
from src.application.cqrs.user.user_di_setup import (
    ExternalEventProvider,
    UserCommandProvider,
    UserQueryProvider,
)
from src.application.services.rbac.rbac_di_setup import RBACProvider
from src.application.services.security.jwt_di_setup import JWTProvider
from src.application.services.session.session_di_setup import SessionManagerProvider
from src.application.services.tasks.task_di_setup import NotificationManagerProvider
from src.infrastructure.db.database_di_setup import (
    SessionProvider,
    TestDatabaseProvider,
)
from src.infrastructure.message_broker.message_broker_di_setup import (
    KafkaConsumerManagerProvider,
    MessageBrokerProvider,
)
from src.infrastructure.repositories.repo_di_setup import (
    RepositoryProvider,
    UnitOfWorkProvider,
)
from src.settings.config import ConfigProvider


def init_test_di_container() -> AsyncContainer:
    return make_async_container(
        ConfigProvider(),
        TestDatabaseProvider(),
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
        ExternalEventProvider(),
        MediatorConfigProvider(),
        KafkaConsumerManagerProvider(),
    )
