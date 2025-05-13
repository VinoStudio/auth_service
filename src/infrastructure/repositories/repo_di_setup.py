from dishka import Provider, Scope, provide
from redis.asyncio import Redis, from_url
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.base.repository import BaseSessionRepository
from src.infrastructure.base.repository.base import SQLAlchemyRepository
from src.infrastructure.base.repository.permission_repo import BasePermissionRepository
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.repository.user_reader import BaseUserReader
from src.infrastructure.base.repository.user_writer import BaseUserWriter
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.db.uow import SQLAlchemyUoW
from src.infrastructure.repositories.oauth.oauth_repo import OAuthAccountRepository
from src.infrastructure.repositories.permission.permission_repo import (
    PermissionRepository,
)
from src.infrastructure.repositories.role.role_invalidation_repo import (
    RoleInvalidationRepository,
)
from src.infrastructure.repositories.role.role_repo import RoleRepository
from src.infrastructure.repositories.session.session_repo import SessionRepository
from src.infrastructure.repositories.token.redis_repo import TokenBlackListRepository
from src.infrastructure.repositories.user.user_reader import UserReader
from src.infrastructure.repositories.user.user_writer import UserWriter
from src.settings import Config


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_sqlalchemy_provider(
        self, session: AsyncSession
    ) -> SQLAlchemyRepository:
        return SQLAlchemyRepository(_session=session)

    @provide(scope=Scope.APP)
    async def get_redis_provider(self, config: Config) -> Redis:
        return from_url(config.redis.redis_url)

    user_reader = provide(UserReader, scope=Scope.REQUEST, provides=BaseUserReader)

    user_writer = provide(UserWriter, scope=Scope.REQUEST, provides=BaseUserWriter)

    role_repo = provide(
        RoleRepository, scope=Scope.REQUEST, provides=BaseRoleRepository
    )

    permission_repo = provide(
        PermissionRepository, scope=Scope.REQUEST, provides=BasePermissionRepository
    )

    session_repo = provide(
        SessionRepository, scope=Scope.REQUEST, provides=BaseSessionRepository
    )

    oauth_account_repo = provide(
        OAuthAccountRepository, scope=Scope.REQUEST, provides=OAuthAccountRepository
    )

    token_repo = provide(
        TokenBlackListRepository, scope=Scope.APP, provides=TokenBlackListRepository
    )

    role_invalidation_repo = provide(
        RoleInvalidationRepository, scope=Scope.APP, provides=RoleInvalidationRepository
    )


class UnitOfWorkProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_sqlalchemy_uow_provider(self, session: AsyncSession) -> UnitOfWork:
        return SQLAlchemyUoW(_session=session)
