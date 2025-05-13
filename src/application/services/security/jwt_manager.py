from dataclasses import dataclass
from datetime import UTC, datetime

from jose import ExpiredSignatureError, JWTError

from src.application import dto
from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol
from src.application.base.security.cookie_manager import BaseCookieManager
from src.application.base.security.jwt_encoder import BaseJWTEncoder
from src.application.base.security.jwt_manager import BaseJWTManager
from src.application.base.security.jwt_payload import BaseJWTPayloadGenerator
from src.application.base.security.jwt_user import JWTUserInterface
from src.application.exceptions import (
    AccessRejectedException,
    TokenExpiredException,
    TokenRevokedException,
    TokenValidationError,
)
from src.application.services.security.security_user import SecurityUser
from src.application.services.security.token_type import TokenType
from src.infrastructure.repositories import TokenBlackListRepository
from src.infrastructure.repositories.role.role_invalidation_repo import (
    RoleInvalidationRepository,
)


@dataclass
class JWTManager(BaseJWTManager):
    """
    The implementation of the JWTManager interface.

    This class handles token creation, refresh operations, cookie management,
    and maintains a token blacklist for revoked access.

    Attributes:
        payload_generator: Component that generates JWT payloads
        jwt_encoder: Component that encodes and decodes JWT tokens
        cookie_manager: Component that manages HTTP cookies
        blacklist_repo: Repository to store and retrieve blacklisted tokens
        role_invalidation: Repository to track invalidated roles
    """

    payload_generator: BaseJWTPayloadGenerator
    jwt_encoder: BaseJWTEncoder
    cookie_manager: BaseCookieManager
    blacklist_repo: TokenBlackListRepository
    role_invalidation: RoleInvalidationRepository

    def create_token_pair(
        self,
        security_user: JWTUserInterface,
    ) -> dto.TokenPair:
        access_payload = self.payload_generator.generate(
            security_user, TokenType.ACCESS.value
        )
        refresh_payload = self.payload_generator.generate(
            security_user, TokenType.REFRESH.value
        )

        access_token = self.jwt_encoder.encode(access_payload)
        refresh_token = self.jwt_encoder.encode(refresh_payload)

        return dto.TokenPair(access_token=access_token, refresh_token=refresh_token)

    def get_token_from_cookie(self, request: RequestProtocol) -> str:
        token = self.cookie_manager.get_cookie(request, "refresh_token")

        if not token:
            raise AccessRejectedException("You must sign in to perform this operation")

        return token

    def set_token_in_cookie(self, response: ResponseProtocol, token: str) -> None:
        self.cookie_manager.set_cookie(
            response=response,
            token=token,
            key="refresh_token",
        )

    @staticmethod
    def get_access_token_from_request(request: RequestProtocol) -> str:
        # Check if Authorization header exists
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise AccessRejectedException("Missing Authorization header")

        # Check if it's a Bearer token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AccessRejectedException(
                "Invalid Authorization header format. Must be 'Bearer {token}'"
            )

        token = parts[1]
        if not token:
            raise AccessRejectedException("Empty token provided")

        return token

    async def validate_token(self, token: str) -> dto.Token:
        try:
            payload = self.jwt_encoder.decode(token)
            token_data: dto.Token = dto.Token(**payload)

            # Check if user access is revoked
            mark = await self.blacklist_repo.get_from_blacklist(token_data.sub)

            if mark is not None:
                blacklist_time = datetime.fromtimestamp(float(mark), tz=UTC)
                token_time = datetime.fromtimestamp(token_data.iat, tz=UTC)

                if token_time < blacklist_time:
                    raise TokenRevokedException(token)

            # Check if user role is invalidated
            for role in token_data.roles:
                invalidated_at = (
                    await self.role_invalidation.get_role_invalidation_time(role)
                )

                if invalidated_at is not None:
                    invalidated_time = datetime.fromtimestamp(
                        float(invalidated_at), tz=UTC
                    )
                    token_time = datetime.fromtimestamp(token_data.iat, tz=UTC)

                    if token_time < invalidated_time:
                        raise TokenRevokedException(token)

        except ExpiredSignatureError as err:
            raise TokenExpiredException(token) from err

        except JWTError as err:
            raise TokenValidationError(token) from err

        else:
            return token_data

    async def refresh_tokens(
        self, request: RequestProtocol, response: ResponseProtocol
    ) -> dto.TokenPair:
        try:
            refresh_token = self.get_token_from_cookie(request)

            token_data: dto.Token = await self.validate_token(refresh_token)

            security_user: JWTUserInterface = SecurityUser.create_from_token_dto(
                token_data
            )

            new_token_pair: dto.TokenPair = self.create_token_pair(
                security_user=security_user
            )
            self.set_token_in_cookie(response, new_token_pair.refresh_token)

        except ValueError as err:
            raise TokenValidationError("") from err

        else:
            return new_token_pair

    async def revoke_token(self, response: ResponseProtocol, token: str) -> None:
        # Clear the refresh token cookie
        self.cookie_manager.delete_cookie(response, "refresh_token")

        # Decode the token to get the user ID
        token_data: dto.Token = dto.Token(**self.jwt_encoder.decode(token))

        # Calculate how many seconds from now until token expiration
        # We add a buffer (e.g., 1 day) to ensure we keep the blacklist entry a bit longer
        current_time = datetime.now(UTC)
        token_exp_dt = datetime.fromtimestamp(token_data.exp, tz=UTC)
        seconds_until_expiry = int((token_exp_dt - current_time).total_seconds()) + (
            24 * 60 * 60
        )  # Add 1 day buffer

        # Add user to blacklist with current timestamp and appropriate expiration
        await self.blacklist_repo.add_to_blacklist(token_data.sub, seconds_until_expiry)
