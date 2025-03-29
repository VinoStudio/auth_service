import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.domain.permission.values import PermissionName
from src.domain.role.values import RoleName
from src.domain.user.entity.user import User
from src.domain.user.values import UserId, Username, Email, Password
from src.infrastructure.base.repository.base import SQLAlchemyRepository
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.repository.user_reader import BaseUserReader
from src.infrastructure.base.repository.user_writer import BaseUserWriter
from src.infrastructure.db.uow import SQLAlchemyUoW
from src.infrastructure.exceptions import UserDoesNotExistException
from src.infrastructure.repositories import UserReader, UserWriter, RoleRepository
from src.infrastructure.repositories.pagination import Pagination
import src.infrastructure.db.models as models
import src.domain as domain


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
        uow: SQLAlchemyUoW = await c.get(SQLAlchemyUoW)

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
        uow: SQLAlchemyUoW = await c.get(SQLAlchemyUoW)

        user_role = await role_repo.get_role_by_name("user")
        moderator_role = await role_repo.get_role_by_name("moderator")

        user = User.create(
            user_id=UserId("test_user_id"),
            username=Username("test_username"),
            email=Email("test_email@test.com"),
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
        uow: SQLAlchemyUoW = await c.get(SQLAlchemyUoW)

        user_role = await role_repo.get_role_by_name("user")
        moderator_role = await role_repo.get_role_by_name("moderator")

        user = User.create(
            user_id=UserId("user_id"),
            username=Username("username"),
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
        uow: SQLAlchemyUoW = await c.get(SQLAlchemyUoW)

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

        updated_db_user = await user_reader.get_user_by_id(user_id=user.id.to_raw())

        assert updated_db_user is not None
        assert admin_role in list(updated_db_user.roles)


"""
Microservice for user authentication, authorization based on JWT mechanism with role-based access control. Project implement Event Driven Arhitecture, CQRS and Kafka as message broker. 
"""


# async def test_user_with_used_username_creation(create_test_user, di_container):
#     user = User.create(
#         UserId("user_id"),
#         Username("username"),
#         FullName("first_name", "last_name", "middle_name"),
#     )
#
#     async with di_container() as c:
#         user_writer = await c.get(BaseUserWriter)
#         with pytest.raises(IntegrityError):
#             user = await user_writer.create_user(user=user)
#
#
# async def test_update_username(create_test_user, di_container):
#     user = User.create(
#         UserId("user_id"),
#         Username("new_username"),
#         FullName("first_name", "last_name", "middle_name"),
#     )
#
#     async with di_container() as c:
#         user_writer = await c.get(BaseUserWriter)
#         user_reader = await c.get(BaseUserReader)
#         uow = await c.get(SQLAlchemyUoW)
#
#         await user_writer.update_user(user=user)
#         await uow.commit()
#
#         updated_user = await user_reader.get_user_by_id(user_id="user_id")
#
#         assert updated_user.username.to_raw() == "new_username"
#
#
# async def test_get_user_by_username(di_container):
#     """Test retrieving a user by username"""
#     async with di_container() as c:
#         user_writer = await c.get(BaseUserWriter)
#         uow = await c.get(SQLAlchemyUoW)
#
#         # Create test user
#         user = User.create(
#             UserId("username_lookup_id"),
#             Username("find_me_by_username"),
#             FullName("Alice", "Johnson", "Marie"),
#         )
#         await user_writer.create_user(user=user)
#         await uow.commit()
#
#     # Get user
#     async with di_container() as c2:
#         user_reader = await c2.get(BaseUserReader)
#
#         # Lookup by username
#         found_user = await user_reader.get_user_by_username(
#             username="find_me_by_username"
#         )
#         assert found_user is not None
#         assert found_user.id.to_raw() == "username_lookup_id"
#         assert found_user.fullname.first_name == "Alice"
#
#
# async def test_user_not_found(di_container):
#     """Test handling non-existent users"""
#     async with di_container() as c:
#         user_reader = await c.get(BaseUserReader)
#
#         # Try to find not existent user then get an exception
#         with pytest.raises(UserDoesNotExistException):
#             await user_reader.get_user_by_id(user_id="does_not_exist")
#
#
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
# async def test_update_full_name(create_test_user, di_container):
#     """Test updating a user's full name"""
#     async with di_container() as c:
#         user_writer = await c.get(BaseUserWriter)
#         user_reader = await c.get(BaseUserReader)
#         uow = await c.get(SQLAlchemyUoW)
#
#         # Get the existing user
#         user = await user_reader.get_user_by_id(user_id="user_id")
#
#         # Update full name
#         user.set_fullname(fullname=FullName("Updated", "Name", "Changed"))
#
#         await user_writer.update_user(user=user)
#         await uow.commit()
#
#     async with di_container() as c:
#         # Verify update
#         user_reader = await c.get(BaseUserReader)
#         result = await user_reader.get_user_by_id(user_id="user_id")
#         assert result.fullname.first_name == "Updated"
#         assert result.fullname.last_name == "Name"
#         assert result.fullname.middle_name == "Changed"
#
#
# async def test_list_all_users(di_container):
#     """Test listing all users with pagination"""
#     async with di_container() as c:
#         user_writer = await c.get(BaseUserWriter)
#         user_reader = await c.get(BaseUserReader)
#         uow = await c.get(SQLAlchemyUoW)
#
#         # Create multiple test users
#         for i in range(5):
#             user = User.create(
#                 UserId(f"list_user_{i}"),
#                 Username(f"list_username_{i}"),
#                 FullName(f"First{i}", f"Last{i}", f"Middle{i}"),
#             )
#             await user_writer.create_user(user=user)
#
#         await uow.commit()
#     async with di_container() as c:
#         user_reader = await c.get(BaseUserReader)
#         pagination1 = Pagination(offset=0, limit=2)
#         pagination2 = Pagination(offset=2, limit=3)
#
#         # Test listing with pagination
#         page_1 = await user_reader.get_all_users(pagination=pagination1)
#         assert len(page_1) == 2
#
#         page_2 = await user_reader.get_all_users(pagination=pagination2)
#         assert len(page_2) == 3
#
#         # Ensure no duplicates between pages
#         page_1_ids = {user.id.to_raw() for user in page_1}
#         page_2_ids = {user.id.to_raw() for user in page_2}
#         assert not page_1_ids.intersection(page_2_ids)
#
#
# async def test_transaction_rollback_on_error(di_container):
#     """Test transaction rollback when an error occurs"""
#     async with di_container() as c:
#         user_writer = await c.get(BaseUserWriter)
#         user_reader = await c.get(BaseUserReader)
#         uow = await c.get(SQLAlchemyUoW)
#
#         # Create initial valid user
#         valid_user = User.create(
#             UserId("rollback_test_id"),
#             Username("rollback_username"),
#             FullName("First", "Last", "Middle"),
#         )
#
#         # Create a duplicate user that will cause integrity error
#         duplicate_user = User.create(
#             UserId("another_id"),
#             Username("rollback_username"),  # Same username will cause conflict
#             FullName("Other", "Person", "Name"),
#         )
#
#         try:
#             # Add both users in the same transaction
#             await user_writer.create_user(user=valid_user)
#             await user_writer.create_user(user=duplicate_user)  # This should fail
#             await uow.commit()
#             pytest.fail("Expected IntegrityError was not raised")
#
#         except IntegrityError:
#             await uow.rollback()
#
#     async with di_container() as c:
#         user_reader = await c.get(BaseUserReader)
#         # Verify that neither user was added (transaction rolled back)
#
#         with pytest.raises(UserDoesNotExistException):
#             await user_reader.get_user_by_id(user_id="another_id")
#
#         with pytest.raises(UserDoesNotExistException):
#             await user_reader.get_user_by_id(user_id="rollback_test_id")
#
#
# async def test_get_all_users(di_container):
#     async with di_container() as c:
#
#         user_writer = await c.get(BaseUserWriter)
#         uow = await c.get(SQLAlchemyUoW)
#
#         # Create multiple test users
#         for i in range(6, 11):
#             user = User.create(
#                 UserId(f"list_user_{i}"),
#                 Username(f"list_username_{i}"),
#                 FullName(f"First{i}", f"Last{i}", f"Middle{i}"),
#             )
#             await user_writer.create_user(user=user)
#
#         await uow.commit()
#
#     async with di_container() as c:
#         user_reader = await c.get(BaseUserReader)
#         pagination: Pagination = Pagination(offset=0, limit=5)
#         users = await user_reader.get_all_users(pagination=pagination)
#         print(users)
#         assert len(users) == 5
