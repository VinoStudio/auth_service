from dishka import provide, Scope, Provider
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.infrastructure.base.repository.base import SQLAlchemyRepository, BaseMemoryRepository
from src.infrastructure.base.repository import BaseSessionRepository
from src.infrastructure.base.repository.user_reader import BaseUserReader
from src.infrastructure.base.repository.user_writer import BaseUserWriter
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.db.uow import SQLAlchemyUoW
from src.infrastructure.repositories.token.redis_repo import TokenBlackListRepository
from src.infrastructure.repositories.session.session_repo import SessionRepository
from src.infrastructure.repositories.user.user_reader import UserReader
from src.infrastructure.repositories.user.user_writer import UserWriter
from src.infrastructure.repositories.role.role_repo import RoleRepository
from src.settings import Config


class RepositoryProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_sqlalchemy_provider(
        self, session: AsyncSession
    ) -> SQLAlchemyRepository:
        return SQLAlchemyRepository(_session=session)

    @provide(scope=Scope.APP)
    async def get_redis_provider(self, config: Config) -> Redis:
        return Redis(host=config.redis.redis_url, port=config.redis.port)

    user_reader = provide(UserReader, scope=Scope.REQUEST, provides=BaseUserReader)

    user_writer = provide(UserWriter, scope=Scope.REQUEST, provides=BaseUserWriter)

    role_repo = provide(RoleRepository, scope=Scope.REQUEST, provides=BaseRoleRepository)

    session_repo = provide(SessionRepository, scope=Scope.REQUEST, provides=BaseSessionRepository)

    token_repo = provide(TokenBlackListRepository, scope=Scope.APP, provides=BaseMemoryRepository)


class UnitOfWorkProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_sqlalchemy_uow_provider(self, session: AsyncSession) -> SQLAlchemyUoW:
        return SQLAlchemyUoW(_session=session)
