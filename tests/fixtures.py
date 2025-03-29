from dishka import AsyncContainer, make_async_container

from src.infrastructure.db.di_setup import TestDatabaseProvider, SessionProvider
from src.infrastructure.message_broker.di_setup import MessageBrokerProvider
from src.infrastructure.repositories.di_setup import (
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
        # MessageBrokerProvider(),
    )


#
# def init_test_di_container() -> AsyncContainer:
#     return get_container()
