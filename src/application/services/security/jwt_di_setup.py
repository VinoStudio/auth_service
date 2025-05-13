from dishka import Provider, Scope, provide

from src.application.base.security import (
    BaseCookieManager,
    BaseJWTEncoder,
    BaseJWTManager,
    BaseJWTPayloadGenerator,
)
from src.application.services.security.cookie_manager import CookieManager
from src.application.services.security.jwt_encoder import JWTEncoder
from src.application.services.security.jwt_manager import JWTManager
from src.application.services.security.jwt_payload_generator import JWTPayloadGenerator
from src.application.services.security.oauth_manager import (
    OAuthManager,
    OAuthProviderFactory,
)
from src.infrastructure.repositories import TokenBlackListRepository
from src.infrastructure.repositories.role.role_invalidation_repo import (
    RoleInvalidationRepository,
)
from src.settings.config import Config


class JWTProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_jwt_encoder(self, config: Config) -> BaseJWTEncoder:
        return JWTEncoder(
            secret_key=config.jwt.secret_key, algorithm=config.jwt.algorithm
        )

    @provide(scope=Scope.APP)
    async def get_jwt_payload_generator(
        self, config: Config
    ) -> BaseJWTPayloadGenerator:
        return JWTPayloadGenerator(
            access_token_expire_minutes=config.jwt.access_token_expire_minutes,
            refresh_token_expire_minutes=config.jwt.refresh_token_expire_minutes,
        )

    @provide(scope=Scope.APP)
    async def get_jwt_cookie_manager(self, config: Config) -> BaseCookieManager:
        return CookieManager(
            cookie_path=config.jwt.cookie_path,
            cookie_secure=config.jwt.secure,
            cookie_httponly=config.jwt.httponly,
            cookie_samesite=config.jwt.samesite,
            cookie_max_age=config.jwt.refresh_token_expire_minutes,
        )

    @provide(scope=Scope.APP)
    async def get_jwt_manager(
        self,
        jwt_encoder: BaseJWTEncoder,
        jwt_payload_generator: BaseJWTPayloadGenerator,
        jwt_cookie_manager: BaseCookieManager,
        black_list_repo: TokenBlackListRepository,
        role_invalidation: RoleInvalidationRepository,
    ) -> BaseJWTManager:
        return JWTManager(
            jwt_encoder=jwt_encoder,
            cookie_manager=jwt_cookie_manager,
            payload_generator=jwt_payload_generator,
            blacklist_repo=black_list_repo,
            role_invalidation=role_invalidation,
        )

    @provide(scope=Scope.APP)
    async def get_oauth_providers(self, config: Config) -> OAuthProviderFactory:
        return OAuthProviderFactory(
            providers={
                "google": config.google_oauth,
                "yandex": config.yandex_oauth,
                "github": config.github_oauth,
            }
        )

    oauth_provider = provide(OAuthManager, scope=Scope.REQUEST)
