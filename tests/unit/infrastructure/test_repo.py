import pytest
from sqlalchemy.exc import IntegrityError

from src import domain
from src.application.dto.user import UserCredentials
from src.domain.permission.values import PermissionName
from src.domain.role.values import RoleName
from src.domain.user.entity.user import User
from src.domain.user.values import Email, Password, UserId, Username
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.repository.user_reader import BaseUserReader
from src.infrastructure.base.repository.user_writer import BaseUserWriter
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.db.uow import SQLAlchemyUoW
from src.infrastructure.exceptions import UserDoesNotExistException
from src.infrastructure.repositories import RoleRepository, UserReader, UserWriter
from src.infrastructure.repositories.pagination import Pagination


async def test_roles_permissions_creation(di_container):
    write: domain.Permission = domain.Permission(PermissionName("write_test"))
    read: domain.Permission = domain.Permission(PermissionName("read_test"))

    user_role: domain.Role = domain.Role(name=RoleName("user_reader"))
    user_role.add_permission(read)

    moderator_role: domain.Role = domain.Role(name=RoleName("moderator_writer"))
    moderator_role.add_permission(read)
    moderator_role.add_permission(write)

    async with di_container() as c:
        role_repo: RoleRepository = await c.get(BaseRoleRepository)
        uow: SQLAlchemyUoW = await c.get(UnitOfWork)

        await role_repo.create_role(role=user_role)
        await role_repo.create_role(role=moderator_role)

        await uow.commit()

    async with di_container() as c:
        role_repo: RoleRepository = await c.get(BaseRoleRepository)

        roles = await role_repo.get_all_roles()

        assert user_role in roles
        assert moderator_role in roles

        permissions = await role_repo.get_role_permissions(role_id=user_role.id)

        assert len(permissions) == 1


async def test_create_user(di_container, create_test_permissions_roles):
    async with di_container() as c:
        user_writer: UserWriter = await c.get(BaseUserWriter)
        role_repo: RoleRepository = await c.get(BaseRoleRepository)
        uow: UnitOfWork = await c.get(UnitOfWork)

        user_role = await role_repo.get_role_by_name("user")
        moderator_role = await role_repo.get_role_by_name("moderator")

        user = User.create(
            user_id=UserId("test_user"),
            username=Username("test_username"),
            email=Email("test_user@test.com"),
            password=Password.create("test_password1SS2"),
            role=user_role,
        )

        user.add_role(moderator_role)

        await user_writer.create_user(user)

        await uow.commit()

    async with di_container() as c:
        user_reader: UserReader = await c.get(BaseUserReader)
        db_user: domain.User = await user_reader.get_user_by_id(
            user_id=user.id.to_raw()
        )

        assert db_user is not None
        assert db_user.id.to_raw() == user.id.to_raw()
        assert db_user.username.to_raw() == user.username.to_raw()
        assert user_role in list(db_user.roles)
        assert moderator_role in list(db_user.roles)

        permissions = await user_reader.get_user_permissions(user_id=user.id.to_raw())

        assert len(permissions) == 2
        assert "read" in permissions
        assert "write" in permissions


async def test_update_user_and_roles(di_container, create_test_permissions_roles):
    async with di_container() as c:
        user_writer: UserWriter = await c.get(BaseUserWriter)
        role_repo: RoleRepository = await c.get(BaseRoleRepository)
        uow: UnitOfWork = await c.get(UnitOfWork)

        user_role = await role_repo.get_role_by_name("user")
        moderator_role = await role_repo.get_role_by_name("moderator")

        user = User.create(
            user_id=UserId("test_user_id"),
            username=Username("username_for_test"),
            email=Email("test@test.com"),
            password=Password.create("test_pord1SS2"),
            role=user_role,
        )

        user.add_role(moderator_role)

        await user_writer.create_user(user)
        await uow.commit()

    async with di_container() as c:
        user_writer: UserWriter = await c.get(BaseUserWriter)
        user_reader: UserReader = await c.get(BaseUserReader)
        role_repo: RoleRepository = await c.get(BaseRoleRepository)
        uow: SQLAlchemyUoW = await c.get(UnitOfWork)

        admin_role = domain.Role(name=RoleName("admin"))
        create_users = domain.Permission(PermissionName("create_users"))
        delete_users = domain.Permission(PermissionName("delete_users"))

        admin_role.add_permission(create_users)
        admin_role.add_permission(delete_users)

        await role_repo.create_role(role=admin_role)
        await uow.commit()

        db_admin_role = await role_repo.get_role_by_name("admin")

        assert db_admin_role is not None
        assert create_users in list(db_admin_role.permission)
        assert delete_users in list(db_admin_role.permission)

        db_user: domain.User = await user_reader.get_user_by_id(
            user_id=user.id.to_raw()
        )

        db_user.add_role(admin_role)

        await user_writer.update_user(user=db_user)
        await uow.commit()

        updated_db_user: domain.User = await user_reader.get_user_by_id(
            user_id=user.id.to_raw()
        )

        assert updated_db_user is not None
        assert admin_role in list(updated_db_user.roles)
        assert updated_db_user.jwt_data

        test_user: UserCredentials = await user_reader.get_user_credentials_by_email(
            email_or_username="test@test.com"
        )

        assert test_user.user_id == updated_db_user.id.to_raw()
        assert test_user.jwt_data == updated_db_user.jwt_data
        assert test_user.hashed_password == updated_db_user.password.to_raw()


async def test_user_with_used_username_creation(
    create_test_permissions_roles, create_test_user, di_container
):
    async with di_container() as c:
        user_writer = await c.get(BaseUserWriter)
        role_repo = await c.get(BaseRoleRepository)
        user_role = await role_repo.get_role_by_name("user")

        user = User.create(
            UserId("user_id"),
            Username("username"),
            Email("test_email@test.com"),
            Password.create("test_password1SS2"),
            role=user_role,
        )

        with pytest.raises(IntegrityError):
            await user_writer.create_user(user=user)


async def test_get_user_by_username(
    create_test_permissions_roles, create_test_user, di_container
):
    """Test retrieving a user by username"""
    # Get user
    async with di_container() as c:
        user_reader = await c.get(BaseUserReader)

        # Lookup by username
        found_user = await user_reader.get_user_by_username(username="username")
        assert found_user is not None
        assert found_user.notification_email.to_raw() == "username"
        assert found_user.id.to_raw() == "user_id"
        assert found_user.deleted_at is None
        assert found_user.roles is not None


async def test_user_not_found(di_container):
    """Test handling non-existent users"""
    async with di_container() as c:
        user_reader = await c.get(BaseUserReader)

        # Try to find not existent user then get an exception
        with pytest.raises(UserDoesNotExistException):
            await user_reader.get_user_by_id(user_id="does_not_exist")


# async def test_delete_user(create_test_user, di_container):
#     """Test deleting a user"""
#     async with di_container() as c:
#         user_writer = await c.get(BaseUserWriter)
#         user_reader = await c.get(BaseUserReader)
#         uow = await c.get(SQLAlchemyUoW)
#
#         # Verify the user exists first
#         existing_user = await user_reader.get_user_by_id(user_id="user_id")
#         assert existing_user is not None
#
#         # Delete the user
#         existing_user.delete()
#         await user_writer.delete_user(existing_user)
#         await uow.commit()
#
#     async with di_container() as c:
#         # Verify deletion
#         user_reader = await c.get(BaseUserReader)
#
#         deleted_user = await user_reader.get_user_by_id(user_id="user_id")
#         assert deleted_user.deleted_at.is_deleted() is True
#
#
# async def test_restore_user_back_to_active(create_test_user, di_container):
#     """Test restoring a user back to active"""
#     async with di_container() as c:
#         user_writer = await c.get(BaseUserWriter)
#         user_reader = await c.get(BaseUserReader)
#         uow = await c.get(SQLAlchemyUoW)
#
#         # Verify the user exists first
#         existing_user = await user_reader.get_user_by_id(user_id="user_id")
#         assert existing_user is not None
#
#         # Restore the user
#         existing_user.restore()
#         await user_writer.restore_user(existing_user)
#         await uow.commit()
#
#     async with di_container() as c:
#         # Verify restoration
#         user_reader = await c.get(BaseUserReader)
#         restored_user = await user_reader.get_user_by_id(user_id="user_id")
#         assert restored_user.deleted_at.is_deleted() is False
#
#
async def test_list_all_users(di_container):
    """Test listing all users with pagination"""
    async with di_container() as c:
        user_writer = await c.get(BaseUserWriter)
        user_reader = await c.get(BaseUserReader)
        role_repo = await c.get(BaseRoleRepository)
        uow = await c.get(UnitOfWork)

        user_role = await role_repo.get_role_by_name("user")

        # Create multiple test users
        for i in range(5):
            user = User.create(
                UserId(f"list_user_{i}"),
                Username(f"list_username_{i}"),
                Email(f"test_email_{i}@test.com"),
                Password.create("test_password1SS2"),
                role=user_role,
            )
            await user_writer.create_user(user=user)

        await uow.commit()
    async with di_container() as c:
        user_reader = await c.get(BaseUserReader)
        pagination1 = Pagination(offset=0, limit=2)
        pagination2 = Pagination(offset=2, limit=3)

        # Test listing with pagination
        page_1 = await user_reader.get_all_users(pagination=pagination1)
        assert len(page_1) == 2

        page_2 = await user_reader.get_all_users(pagination=pagination2)
        assert len(page_2) == 3

        # Ensure no duplicates between pages
        page_1_ids = {user.id.to_raw() for user in page_1}
        page_2_ids = {user.id.to_raw() for user in page_2}
        assert not page_1_ids.intersection(page_2_ids)


async def test_transaction_rollback_on_error(di_container):
    """Test transaction rollback when an error occurs"""
    async with di_container() as c:
        user_writer = await c.get(BaseUserWriter)
        user_reader = await c.get(BaseUserReader)
        role_repo = await c.get(BaseRoleRepository)
        uow = await c.get(UnitOfWork)

        user_role = await role_repo.get_role_by_name("user")

        # Create initial valid user
        valid_user = User.create(
            UserId("rollback_test_id"),
            Username("rollback_username"),
            Email("rollback_email@test.com"),
            Password.create("test_password1SS2"),
            role=user_role,
        )

        # Create a duplicate user that will cause integrity error
        duplicate_user = User.create(
            UserId("another_id"),
            Username("rollback_username"),  # Same username will cause conflict
            Email("rollback2_email@test.com"),
            Password.create("test_password1SS2"),
            role=user_role,
        )

        try:
            # Add both users in the same transaction
            await user_writer.create_user(user=valid_user)
            await user_writer.create_user(user=duplicate_user)  # This should fail
            await uow.commit()
            pytest.fail("Expected IntegrityError was not raised")

        except IntegrityError:
            await uow.rollback()

    async with di_container() as c:
        user_reader = await c.get(BaseUserReader)
        # Verify that neither user was added (transaction rolled back)

        with pytest.raises(UserDoesNotExistException):
            await user_reader.get_user_by_id(user_id="another_id")

        with pytest.raises(UserDoesNotExistException):
            await user_reader.get_user_by_id(user_id="rollback_test_id")


async def test_get_all_users(di_container):
    async with di_container() as c:
        user_writer = await c.get(BaseUserWriter)
        role_repo = await c.get(BaseRoleRepository)
        uow = await c.get(UnitOfWork)

        user_role = await role_repo.get_role_by_name("user")

        # Create multiple test users
        for i in range(6, 11):
            user = User.create(
                UserId(f"list_user_{i}"),
                Username(f"list_username_{i}"),
                Email(f"test_email_{i}@test.com"),
                Password.create("test_password1SS2"),
                role=user_role,
            )
            await user_writer.create_user(user=user)

        await uow.commit()

    async with di_container() as c:
        user_reader = await c.get(BaseUserReader)
        pagination: Pagination = Pagination(offset=0, limit=5)
        users = await user_reader.get_all_users(pagination=pagination)
        assert len(users) == 5


#
# async def test_create_user_session(
#     di_container, create_test_permissions_roles, create_test_user
# ):
#     async with di_container() as c:
#         user_reader = await c.get(BaseUserReader)
#         user_writer = await c.get(BaseUserWriter)
#         uow = await c.get(SQLAlchemyUoW)
#
#         user: domain.User = await user_reader.get_user_by_id(user_id="user_id")
#
#         session = domain.Session(
#             user_id=user.id.to_raw(),
#             device_info="test_device_info",
#             device_id=b"test_device_id".decode("utf-8"),
#             user_agent="test_user_agent",
#         )
#
#         user.add_session(session)
#
#         await user_writer.update_user(user)
#
#         await uow.commit()
#
#     async with di_container() as c:
#         user_reader = await c.get(BaseUserReader)
#
#         db_user: domain.User = await user_reader.get_user_by_id(user_id="user_id")
#
#         assert db_user.sessions is not None
#         assert len(db_user.sessions) == 2
#
#         assert session in list(db_user.sessions)
#
#
# async def test_create_two_user_sessions(
#     di_container, create_test_permissions_roles, create_test_user
# ):
#     async with di_container() as c:
#         user_reader = await c.get(BaseUserReader)
#         user_writer = await c.get(BaseUserWriter)
#         uow = await c.get(SQLAlchemyUoW)
#
#         user: domain.User = await user_reader.get_user_by_id(user_id="user_id")
#
#         session1 = domain.Session(
#             user_id=user.id.to_raw(),
#             device_info="test_device_info",
#             device_id=b"test_device_id".decode("utf-8"),
#             user_agent="test_user_agent",
#         )
#
#         user.add_session(session1)
#
#         session2 = domain.Session(
#             user_id=user.id.to_raw(),
#             device_info="test_device_info",
#             device_id=b"test_device_id".decode("utf-8"),
#             user_agent="arch_linux",
#         )
#
#         user.add_session(session2)
#
#         assert len(user.sessions) == 2
#
#         await user_writer.update_user(user)
#
#         await uow.commit()
#
#     async with di_container() as c:
#         user_reader = await c.get(BaseUserReader)
#         uow = await c.get(SQLAlchemyUoW)
#
#         db_user: domain.User = await user_reader.get_user_by_id(user_id="user_id")
#
#         assert db_user.sessions is not None
#         assert len(db_user.sessions) == 1
#         assert db_user._sessions.pop().last_activity == session2.last_activity
