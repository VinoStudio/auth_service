from functools import lru_cache

from dishka import AsyncContainer, make_async_container

from application.di_setup import MediatorProvider, MediatorConfigProvider
from application.user.di_setup import (
    CommandRegisterProvider,
    EventRegisterProvider,
    QueryRegisterProvider,
)
from infrastructure.db.di_setup import DatabaseProvider, SessionProvider
from infrastructure.message_broker.di_setup import MessageBrokerProvider
from infrastructure.repositories.di_setup import RepositoryProvider, UnitOfWorkProvider
from settings.config import ConfigProvider


@lru_cache(maxsize=1)
def get_container() -> AsyncContainer:
    return make_async_container(
        ConfigProvider(),
        DatabaseProvider(),
        SessionProvider(),
        RepositoryProvider(),
        UnitOfWorkProvider(),
        MessageBrokerProvider(),
        MediatorProvider(),
        CommandRegisterProvider(),
        EventRegisterProvider(),
        QueryRegisterProvider(),
        MediatorConfigProvider(),
    )
