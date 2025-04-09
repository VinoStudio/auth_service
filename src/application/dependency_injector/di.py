from functools import lru_cache

from dishka import AsyncContainer, make_async_container

from src.application.cqrs.cqrs_di_setup import MediatorProvider, MediatorConfigProvider
from src.application.cqrs.user.user_di_setup import UserCommandProvider
from src.application.cqrs.role.role_di_setup import RoleCommandProvider
from src.application.services.session.session_di_setup import SessionManagerProvider
from src.application.services.security.jwt_di_setup import JWTProvider
from src.application.services.rbac.rbac_di_setup import RBACProvider

from src.infrastructure.db.di_setup import DatabaseProvider, SessionProvider
from src.infrastructure.message_broker.di_setup import MessageBrokerProvider
from src.infrastructure.repositories.di_setup import (
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
        MediatorProvider(),
        UserCommandProvider(),
        RoleCommandProvider(),
        MediatorConfigProvider(),
    )
