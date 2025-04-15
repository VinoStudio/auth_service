from datetime import timedelta, datetime, UTC

from src.application.base.security import BaseJWTManager
from src.application.dto.token import TokenPair, Token
from src.application.exceptions import (
    TokenExpiredException,
    TokenRevokedException,
    TokenValidationError,
)
from src.application.services.rbac.rbac_manager import RBACManager
from src.application.services.security.jwt_manager import JWTManager
from src.application.services.security.security_user import SecurityUser
from src.application.services.security.token_type import TokenType
from src.infrastructure.base.repository import BaseUserReader
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.repositories import TokenBlackListRepository, UserReader

from tests.mock.response import MockResponse
from tests.mock.request import MockRequest

import pytest
import src.domain as domain
import src.application.dto as dto


async def test_create_token_pair(
    di_container, create_test_permissions_roles, create_test_user
):

    async with di_container() as c:

        jwt_manager = await c.get(BaseJWTManager)
        user_reader = await c.get(BaseUserReader)

        user: domain.User = await user_reader.get_user_by_id(user_id="user_id")

        security_user = SecurityUser.create_from_domain_user(user)
        security_user.set_device_id("device_id")

        test_response = MockResponse()

        # Execute
        token_pair: dto.TokenPair = jwt_manager.create_token_pair(
            security_user, test_response
        )

        # Verify
        assert isinstance(token_pair, TokenPair)
        assert token_pair.access_token
        assert token_pair.refresh_token

        access_payload = jwt_manager.jwt_encoder.decode(token_pair.access_token)
        assert access_payload["sub"] == "user_id"
        assert access_payload["type"] == TokenType.ACCESS.value
        assert access_payload["roles"] == ["user"]
        assert access_payload["permissions"] == ["content:view"]
        assert access_payload["did"] == "device_id"
        assert "jti" in access_payload
        assert "exp" in access_payload
        assert "iat" in access_payload
        assert "did" in access_payload
        assert "lvl" in access_payload

        refresh_payload = jwt_manager.jwt_encoder.decode(token_pair.refresh_token)
        assert refresh_payload["type"] == TokenType.REFRESH.value
        assert refresh_payload["jti"] != access_payload["jti"]
        assert refresh_payload["exp"] > access_payload["exp"]

        assert refresh_payload["sub"] == "user_id"
        assert refresh_payload["roles"] == ["user"]
        assert refresh_payload["permissions"] == ["content:view"]

        assert test_response.cookies["refresh_token"] == token_pair.refresh_token


async def test_validate_token_with_valid_token(di_container):

    async with di_container() as c:
        jwt_manager = await c.get(BaseJWTManager)

        # Create a valid token
        now = datetime.now(UTC)
        payload = {
            "sub": "test123",
            "type": TokenType.ACCESS.value,
            "roles": ["user"],
            "did": "device_id",
            "lvl": 5,
            "permissions": ["content:view"],
            "iat": now.timestamp(),
            "exp": (now + timedelta(minutes=15)).timestamp(),
            "jti": "test-uuid",
        }
        token = jwt_manager.jwt_encoder.encode(payload)

        # Execute
        token_data: Token = await jwt_manager.validate_token(token)

        # Verify
        assert token_data.sub == "test123"
        assert token_data.type == TokenType.ACCESS.value
        assert token_data.roles == ["user"]
        assert token_data.permissions == ["content:view"]


async def test_validate_token_with_expired_token(di_container):

    async with di_container() as c:
        jwt_manager = await c.get(BaseJWTManager)

        # Create an expired token
        now = datetime.now(UTC)
        payload = {
            "sub": "test123",
            "type": TokenType.ACCESS.value,
            "roles": ["user"],
            "did": "device_id",
            "permissions": ["read"],
            "iat": (now - timedelta(minutes=30)).timestamp(),
            "exp": (now - timedelta(minutes=15)).timestamp(),
            "jti": "test-uuid",
        }
        token = jwt_manager.jwt_encoder.encode(payload)

        # Execute & Verify
        with pytest.raises(TokenExpiredException):
            await jwt_manager.validate_token(token)


async def test_validate_token_with_revoked_token(di_container):

    async with di_container() as c:
        jwt_manager: JWTManager = await c.get(BaseJWTManager)
        blacklist_repo = await c.get(TokenBlackListRepository)

        # Create a token issued in the past
        now = datetime.now(UTC)
        token_issue_time = (now - timedelta(hours=2)).timestamp()
        payload = {
            "sub": "test123",
            "type": TokenType.ACCESS.value,
            "roles": ["user"],
            "did": "device_id",
            "lvl": 5,
            "permissions": ["content:view"],
            "iat": token_issue_time,
            "exp": (now + timedelta(minutes=15)).timestamp(),
            "jti": "test-uuid",
        }
        token = jwt_manager.jwt_encoder.encode(payload)

        blacklist_time = int((now - timedelta(hours=1)).timestamp())
        await blacklist_repo.add_to_blacklist("test123", blacklist_time)

        # Execute & Verify
        with pytest.raises(TokenRevokedException):
            await jwt_manager.validate_token(token)


async def test_validate_token_with_invalid_token(di_container):
    async with di_container() as c:
        jwt_manager: JWTManager = await c.get(BaseJWTManager)

    # Execute & Verify
    with pytest.raises(TokenValidationError):
        await jwt_manager.validate_token("invalid.token.format")


async def test_validate_token_with_blacklisted_role(
    di_container,
    create_test_permissions_roles,
    create_test_user,
    get_security_project_manager,
):
    async with di_container() as c:
        jwt_manager: JWTManager = await c.get(BaseJWTManager)
        user_reader: UserReader = await c.get(BaseUserReader)
        rbac_manager: RBACManager = await c.get(RBACManager)
        uow = await c.get(UnitOfWork)

        user: dto.UserCredentials = (
            await user_reader.get_user_credentials_by_email_or_username(
                "test_email@test.com"
            )
        )

        security_user = SecurityUser.create_from_jwt_data(
            jwt_data=user.jwt_data,
        )

        test_response = MockResponse()

        # Execute
        token_pair: dto.TokenPair = jwt_manager.create_token_pair(
            security_user, test_response
        )

        # Update role permissions
        user_role = await rbac_manager.get_role(
            role_name="user", request_from=get_security_project_manager
        )

        permission = await rbac_manager.get_permission(
            permission_name="project:view", request_from=get_security_project_manager
        )

        user_role.add_permission(permission)

        await rbac_manager.update_role(
            role=user_role, request_from=get_security_project_manager
        )
        await rbac_manager.invalidate_role(user_role.name.to_raw())

        await uow.commit()

        # Verify
        with pytest.raises(TokenRevokedException):
            await jwt_manager.validate_token(test_response.cookies["refresh_token"])
