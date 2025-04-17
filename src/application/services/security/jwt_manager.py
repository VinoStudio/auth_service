from datetime import datetime, UTC

from src.application.base.interface.request import RequestProtocol
from src.application.base.interface.response import ResponseProtocol
from src.application.base.security.cookie_manager import BaseCookieManager
from src.application.base.security.jwt_encoder import BaseJWTEncoder
from src.application.base.security.jwt_manager import BaseJWTManager
from src.application.base.security.jwt_payload import BaseJWTPayloadGenerator
from src.application.base.security.jwt_user import JWTUserInterface
from src.application.exceptions import (
    TokenRevokedException,
    TokenExpiredException,
    TokenValidationError,
    AccessRejectedException,
)
from src.application.services.security.security_user import SecurityUser
from src.application.services.security.token_type import TokenType
from src.infrastructure.repositories import TokenBlackListRepository

from dataclasses import dataclass
from jose import JWTError, ExpiredSignatureError

import src.application.dto as dto
from src.infrastructure.repositories.role.role_invalidation_repo import (
    RoleInvalidationRepository,
)


@dataclass
class JWTManager(BaseJWTManager):
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
        """
        Extract and return the refresh token from the request's cookie.

        Args:
            request: The HTTP request object (Litestar request)

        Returns:
            str: The refresh token

        Raises:
            AccessRejectedException: If the token is missing.
        """

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
    def get_access_token_from_request(request) -> str:
        """
        Extract and return the access token from the request's Authorization header.

        Args:
            request: The HTTP request object (Litestar request)

        Returns:
            str: The access token

        Raises:
            AccessRejectedException: If the token is missing or wrongly formatted.
        """

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
        """

        If user logout/banned/deleted our command/event should've store user_id in blacklist with timestamp.
        So we check if current token iat is less than blacklist timestamp we raise TokenRevokedException that leads
        to 403 exception from application and tells front-end he should re-login.

        Point is use connection to database less often.

        """

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

            return token_data

        except ExpiredSignatureError:
            raise TokenExpiredException(token)

        except JWTError:
            raise TokenValidationError(token)

    async def refresh_tokens(
        self, request: RequestProtocol, response: ResponseProtocol
    ) -> dto.TokenPair:
        """

        I do not see a reason to validate user using database, because it will be the same that using session based
        authentication. Just store user_id in memory storage when user: banned/deleted/permissions-role changed etc...

        """

        try:
            refresh_token = self.get_token_from_cookie(request)

            token_data: dto.Token = await self.validate_token(refresh_token)

            security_user: JWTUserInterface = SecurityUser.create_from_token_dto(
                token_data
            )

            if not security_user:
                raise ValueError("Invalid session: missing subject")

            new_token_pair: dto.TokenPair = self.create_token_pair(
                security_user=security_user
            )
            self.set_token_in_cookie(response, new_token_pair.refresh_token)

            return new_token_pair

        except ValueError as e:
            raise ValueError(f"Token refresh failed: {str(e)}")

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
