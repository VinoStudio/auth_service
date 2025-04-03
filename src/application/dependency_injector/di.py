from functools import lru_cache

from dishka import AsyncContainer, make_async_container

from src.application.cqrs_di_setup import MediatorProvider, MediatorConfigProvider
from src.application.user.user_di_setup import UserCommandProvider
from src.application.session.session_di_setup import SessionManagerProvider
from src.application.security.jwt_di_setup import JWTProvider

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
        SessionManagerProvider(),
        MediatorProvider(),
        UserCommandProvider(),
        MediatorConfigProvider(),
    )
