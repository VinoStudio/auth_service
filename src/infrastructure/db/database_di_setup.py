from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.infrastructure.db.setup import build_engine, build_session_factory
from src.settings.config import Config


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self, config: Config) -> AsyncEngine:
        engine = await build_engine(config)
        return engine

    @provide(scope=Scope.APP)
    async def get_session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
        return build_session_factory(engine)


class TestDatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self, config: Config) -> AsyncEngine:
        engine = create_async_engine(
            config.test_db.db_url,
            echo=True,
            pool_size=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            max_overflow=15,
        )
        return engine

    @provide(scope=Scope.APP)
    async def get_session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
        return build_session_factory(engine)


class SessionProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            yield session
