import pytest
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy import text

from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.repository.user_writer import BaseUserWriter
from src.infrastructure.db.uow import SQLAlchemyUoW
from tests.fixtures import init_test_di_container
from src.infrastructure.db.models import BaseModel
from src.infrastructure.repositories import RoleRepository

from src.domain.user.entity.user import User
from src.domain.user.values import (
    Email,
    Password,
    UserId,
    Username,
)
from src.domain.permission.entity.permission import Permission
from src.domain.permission.values.permission_name import PermissionName
from src.domain.role.entity.role import Role
from src.domain.role.values.role_name import RoleName


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


@pytest.fixture(scope="session")
async def create_test_permissions_roles():
    container = init_test_di_container()

    write: Permission = Permission(PermissionName("write"))
    read: Permission = Permission(PermissionName("read"))

    user_role: Role = Role(name=RoleName("user"))

    moderator: Role = Role(name=RoleName("moderator"))

    async with container() as c:
        role_repo: RoleRepository = await c.get(BaseRoleRepository)
        uow: SQLAlchemyUoW = await c.get(SQLAlchemyUoW)

        await role_repo.create_role(role=user_role)
        await role_repo.create_role(role=moderator)
        await role_repo.create_permission(permission=write)
        await role_repo.create_permission(permission=read)

        await role_repo.set_role_permission(role_id=user_role.id, permission_id=read.id)

        await role_repo.set_role_permission(
            role_id=moderator.id, permission_id=write.id
        )
        await role_repo.set_role_permission(role_id=moderator.id, permission_id=read.id)

        await uow.commit()


# @pytest.fixture(scope="session")
# async def create_test_user():
#     container = init_test_di_container()
#
#     async with container() as c:
#         user_writer = await c.get(BaseUserWriter)
#         uow = await c.get(SQLAlchemyUoW)
#
#         await user_writer.create_user(
#             User.create(
#                 UserId("user_id"),
#                 Username("username"),
#                 FullName("first_name", "last_name", "middle_name"),
#             )
#         )
#         await uow.commit()


@pytest.fixture(scope="session")
async def di_container():
    return init_test_di_container()
