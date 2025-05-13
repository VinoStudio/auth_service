from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.settings.config import Config


@lru_cache(maxsize=1)
async def build_engine(config: Config) -> AsyncEngine:
    # don't forget to dispose connection pools at app shutdown
    return create_async_engine(
        config.postgres.db_url,
        echo=True,
        pool_size=50,
    )


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
