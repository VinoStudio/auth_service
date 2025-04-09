import pytest
import asyncio
from uuid6 import uuid7

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy import text

from src.domain.role.entity.role_catalog import SystemRoles
from src.infrastructure.base.repository import BaseUserReader
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.repository.user_writer import BaseUserWriter
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.db.uow import SQLAlchemyUoW
from tests.fixtures import init_test_di_container
from src.infrastructure.db.models import BaseModel
from src.infrastructure.repositories import RoleRepository, UserReader

from src.application.services.security.jwt_manager import JWTManager
from src.application.base.security.jwt_manager import BaseJWTManager
from src.application.services.security.security_user import SecurityUser

from src.domain.user.entity.user import User
from src.domain.user.values import (
    Email,
    Password,
    UserId,
    Username,
)
from tests.mock.response import MockResponse
from tests.mock.request import MockRequest

import src.domain as domain
import src.application.dto as dto


# from fastapi.testclient import TestClient
# from httpx import AsyncClient, ASGITransport
# from presentation.api.main import create_app

# app = create_app()
# app.dependency_overrides[get_container] = init_test_di_container
#
# client = TestClient(app=app)


# @pytest.fixture(scope="session")
# async def test_client():
#     return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.fixture(scope="session")
async def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def create_test_database():
    container = init_test_di_container()

    engine = await container.get(AsyncEngine)

    # Create tables inside this context
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield

    # Drop tables inside this context
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def create_test_permissions_roles():

    container = init_test_di_container()

    async with container() as c:
        role_repo = await c.get(BaseRoleRepository)
        user_writer = await c.get(BaseUserWriter)
        uow = await c.get(UnitOfWork)

        super_role = await role_repo.check_role_exists("super_admin")
        if super_role:
            print("Roles already exist, skipping seed")
            return

        for role in SystemRoles.get_all_roles():
            await role_repo.create_role(role=role)
            await uow.commit()

        if not super_role:
            super_role = await role_repo.get_role_by_name("super_admin")

        super_user = domain.User.create(
            user_id=UserId(str(uuid7())),
            email=Email("test@admin.com"),
            username=Username("super_admin"),
            password=Password.create("admin1SS"),
            role=super_role,
        )

        await user_writer.create_user(super_user)
        await uow.commit()


@pytest.fixture(scope="session")
async def create_test_user():
    container = init_test_di_container()

    async with container() as c:
        user_writer = await c.get(BaseUserWriter)
        role_repo = await c.get(BaseRoleRepository)
        uow = await c.get(UnitOfWork)

        await user_writer.create_user(
            User.create(
                UserId("user_id"),
                Username("username"),
                Email("test_email@test.com"),
                Password.create("test_password1SS2"),
                await role_repo.get_role_by_name("user"),
            )
        )
        await uow.commit()


@pytest.fixture(scope="session")
async def mock_admin_request():
    container = init_test_di_container()
    test_request = MockRequest()

    async with container() as c:
        jwt_manager: JWTManager = await c.get(BaseJWTManager)
        role_repo = await c.get(BaseRoleRepository)
        user_reader = await c.get(BaseUserReader)

        user_credentials: dto.UserCredentials = (
            await user_reader.get_user_credentials_by_email_or_username(
                "test@admin.com"
            )
        )

        security_user = SecurityUser.create_from_jwt_data(
            jwt_data=user_credentials.jwt_data,
        )

        tokens = jwt_manager.create_token_pair(
            security_user=security_user,
            response=test_request,  # type: ignore
        )

    return test_request


@pytest.fixture(scope="session")
async def get_security_admin():
    container = init_test_di_container()
    async with container() as c:
        user_reader = await c.get(BaseUserReader)
        user_credentials: dto.UserCredentials = (
            await user_reader.get_user_credentials_by_email_or_username(
                "test@admin.com"
            )
        )

        security_user = SecurityUser.create_from_jwt_data(
            jwt_data=user_credentials.jwt_data,
        )

    return security_user


@pytest.fixture(scope="session")
async def get_security_user(create_test_user):
    container = init_test_di_container()
    async with container() as c:
        user_reader = await c.get(BaseUserReader)
        user_credentials: dto.UserCredentials = (
            await user_reader.get_user_credentials_by_email_or_username(
                "test_email@test.com"
            )
        )

        security_user = SecurityUser.create_from_jwt_data(
            jwt_data=user_credentials.jwt_data,
        )

    return security_user


@pytest.fixture(scope="session")
async def get_security_project_manager():
    container = init_test_di_container()
    async with container() as c:
        user_reader = await c.get(BaseUserReader)
        user_writer = await c.get(BaseUserWriter)
        role_repo = await c.get(BaseRoleRepository)
        uow = await c.get(UnitOfWork)

        project_manager = domain.User.create(
            user_id=UserId(str(uuid7())),
            email=Email("test_project_manager_email@test.com"),
            username=Username("test_project_manager"),
            password=Password.create("test_password1SS2"),
            role=await role_repo.get_role_by_name("project_manager"),
        )

        await user_writer.create_user(project_manager)
        await uow.commit()

        user_credentials: dto.UserCredentials = (
            await user_reader.get_user_credentials_by_email_or_username(
                "test_project_manager_email@test.com"
            )
        )

        security_user = SecurityUser.create_from_jwt_data(
            jwt_data=user_credentials.jwt_data,
        )

    return security_user


@pytest.fixture(scope="session")
async def mock_response():
    return MockResponse()


@pytest.fixture(scope="session")
async def di_container():
    return init_test_di_container()
