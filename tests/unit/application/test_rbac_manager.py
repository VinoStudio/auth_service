import pytest

from src import domain
from src.application import dto
from src.application.exceptions.rbac import (
    AccessDeniedException,
    PermissionAlreadyExistsException,
    PermissionInUseException,
    RBACException,
    RoleAlreadyExistsException,
    RoleInUseException,
)
from src.application.services.rbac.rbac_manager import RBACManager
from src.infrastructure.base.repository import BaseUserReader, BaseUserWriter
from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.exceptions.repository import (
    PermissionDoesNotExistException,
)


async def test_get_role_by_admin(di_container, get_security_admin):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)

        role: domain.Role = await rbac_manager.get_role(
            role_name="user", request_from=get_security_admin
        )

        assert role.name.to_raw() == "user"
        assert role.security_level == 8

        assert len(role.permission) != 0


async def test_get_role_by_user(di_container, get_security_user):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)

        with pytest.raises(RBACException):
            await rbac_manager.get_role(
                role_name="user", request_from=get_security_user
            )


async def test_create_role_by_admin(di_container, get_security_admin):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        uow = await c.get(UnitOfWork)

        new_role_dto = dto.RoleCreation(
            name="test_role",
            description="Test role for RBAC",
            security_level=5,
            permissions=["role:view", "user:view"],
        )

        await rbac_manager.create_role(
            role_dto=new_role_dto, request_from=get_security_admin
        )
        await uow.commit()

        role = await rbac_manager.get_role(
            role_name="test_role", request_from=get_security_admin
        )

        assert role.name.to_raw() == "test_role"
        assert role.description == "Test role for RBAC"
        assert role.security_level == 5
        assert any(p.permission_name.to_raw() == "role:view" for p in role.permission)


async def test_create_duplicate_role(di_container, get_security_admin):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        uow = await c.get(UnitOfWork)

        # First create a role
        new_role_dto = dto.RoleCreation(
            name="duplicate_role",
            description="Test role",
            security_level=5,
            permissions=[],
        )

        await rbac_manager.create_role(
            role_dto=new_role_dto, request_from=get_security_admin
        )
        await uow.commit()

        # Try to create the same role again
        with pytest.raises(RoleAlreadyExistsException):
            await rbac_manager.create_role(
                role_dto=new_role_dto, request_from=get_security_admin
            )


async def test_create_role_with_higher_security_level(
    di_container, get_security_project_manager
):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)

        # Assuming get_security_user has lower security level
        new_role_dto = dto.RoleCreation(
            name="high_security_role",
            description="High security role",
            security_level=1,
            permissions=[],
        )
        with pytest.raises(AccessDeniedException):
            await rbac_manager.create_role(
                role_dto=new_role_dto, request_from=get_security_project_manager
            )


async def test_create_new_super_admin_role(di_container, get_security_admin):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        uow = await c.get(UnitOfWork)

        new_role_dto = dto.RoleCreation(
            name="high_security_role",
            description="High security role",
            security_level=0,
            permissions=[],
        )

        with pytest.raises(AccessDeniedException):
            await rbac_manager.create_role(
                role_dto=new_role_dto, request_from=get_security_admin
            )
            uow.commit()


async def test_create_lower_role_with_high_tier_permissions(
    di_container, get_security_project_manager
):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        uow = await c.get(UnitOfWork)

        new_role_dto = dto.RoleCreation(
            name="low_security_role",
            description="Low security role",
            security_level=8,
            permissions=["user:view", "role:create", "role:delete", "role:update"],
        )
        with pytest.raises(AccessDeniedException):
            await rbac_manager.create_role(
                role_dto=new_role_dto, request_from=get_security_project_manager
            )
            await uow.commit()


async def test_create_role_with_permissions_that_requested_dont_have(
    di_container, get_security_project_manager
):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        uow = await c.get(UnitOfWork)

        new_role_dto = dto.RoleCreation(
            name="low_security_role",
            description="Low security role",
            security_level=8,
            permissions=["audit:view"],
        )
        with pytest.raises(AccessDeniedException):
            await rbac_manager.create_role(
                role_dto=new_role_dto, request_from=get_security_project_manager
            )
            await uow.commit()


async def test_update_role_by_admin(di_container, get_security_admin):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        uow = await c.get(UnitOfWork)

        # First get an existing role
        role = await rbac_manager.get_role(
            role_name="user", request_from=get_security_admin
        )

        # Update its description
        original_description = role.description
        role.description = "Updated description"

        await rbac_manager.update_role(role=role, request_from=get_security_admin)

        await rbac_manager.invalidate_role(role.name.to_raw())

        await uow.commit()

    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)

        role = await rbac_manager.get_role(
            role_name="user", request_from=get_security_admin
        )

        assert role.description == "Updated description"
        assert role.description != original_description

        role_mark = await rbac_manager.role_invalidation.get_role_invalidation_time(
            role.name.to_raw()
        )

        assert role_mark is not None
        assert isinstance(role_mark, str)


async def test_update_role_with_high_tier_permissions(
    di_container, get_security_project_manager
):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        uow = await c.get(UnitOfWork)

        # First get an existing role
        role = await rbac_manager.get_role(
            role_name="user", request_from=get_security_project_manager
        )

        # cannot interact with roles having higher security level than yours
        with pytest.raises(AccessDeniedException):
            permission = await rbac_manager.get_permission(
                permission_name="role:update", request_from=get_security_project_manager
            )
            role.add_permission(permission)
            await uow.commit()


async def test_delete_role_in_use_by_admin(di_container, get_security_admin):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)

        user_role: domain.Role = await rbac_manager.get_role(
            role_name="user", request_from=get_security_admin
        )
        with pytest.raises(RoleInUseException):
            await rbac_manager.delete_role(
                role=user_role, request_from=get_security_admin
            )


async def test_delete_permission_in_use_by_admin(di_container, get_security_admin):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)

        permission = await rbac_manager.get_permission(
            permission_name="role:view", request_from=get_security_admin
        )

        with pytest.raises(PermissionInUseException):
            await rbac_manager.delete_permission(
                permission=permission, request_from=get_security_admin
            )


async def test_create_and_delete_permission(di_container, get_security_admin):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        uow = await c.get(UnitOfWork)

        # Create a new permission
        perm_dto = dto.PermissionCreation(name="test:permission")

        permission = await rbac_manager.create_permission(
            permission_dto=perm_dto, request_from=get_security_admin
        )
        await uow.commit()

        assert permission.permission_name.to_raw() == "test:permission"

        # Now delete it (since it's not in use)
        await rbac_manager.delete_permission(
            permission=permission, request_from=get_security_admin
        )

        # Verify it's gone
        with pytest.raises(PermissionDoesNotExistException):
            await rbac_manager.get_permission(
                permission_name="test:permission", request_from=get_security_admin
            )


async def test_create_duplicate_permission(di_container, get_security_admin):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        uow = await c.get(UnitOfWork)

        # Create a permission
        perm_dto = dto.PermissionCreation(name="duplicate:permission")

        await rbac_manager.create_permission(
            permission_dto=perm_dto, request_from=get_security_admin
        )
        await uow.commit()

        # Try to create it again
        with pytest.raises(PermissionAlreadyExistsException):
            await rbac_manager.create_permission(
                permission_dto=perm_dto, request_from=get_security_admin
            )


async def test_assign_and_remove_role_from_user(
    di_container, get_security_admin, create_test_user
):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        user_reader: BaseUserReader = await c.get(BaseUserReader)
        user_writer: BaseUserWriter = await c.get(BaseUserWriter)
        uow = await c.get(UnitOfWork)

        # Get a test user
        user = await user_reader.get_user_by_email("test_email@test.com")

        # Create a test role to assign
        role_dto = dto.RoleCreation(
            name="test_assignable_role",
            description="Role for assignment testing",
            security_level=5,
            permissions=[],
        )

        new_role = await rbac_manager.create_role(
            role_dto=role_dto, request_from=get_security_admin
        )
        await uow.commit()

        # Assign role to user
        updated_user = await rbac_manager.assign_role_to_user(
            user=user, role=new_role, request_from=get_security_admin
        )

        await user_writer.update_user(updated_user)
        await uow.commit()

    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        user_reader: BaseUserReader = await c.get(BaseUserReader)
        user_writer: BaseUserWriter = await c.get(BaseUserWriter)
        uow = await c.get(UnitOfWork)

        updated_user_from_db = await user_reader.get_user_by_email(
            "test_email@test.com"
        )

        assert updated_user.id == updated_user_from_db.id
        assert new_role in updated_user.roles

        # Remove role from user
        updated_user = await rbac_manager.remove_role_from_user(
            user=updated_user_from_db, role=new_role, request_from=get_security_admin
        )

        await user_writer.update_user(updated_user)
        await uow.commit()

    async with di_container() as c:
        user_reader: BaseUserReader = await c.get(BaseUserReader)

        updated_user = await user_reader.get_user_by_email("test_email@test.com")

        # Verify role was removed
        assert new_role not in updated_user.roles


async def test_system_role_access_override(
    di_container, get_security_admin, get_security_project_manager
):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        uow: UnitOfWork = await c.get(UnitOfWork)

        # Create a role that requires high security level
        high_security_role_dto = dto.RoleCreation(
            name="high_level_role",
            description="High security role",
            security_level=1,
            permissions=[],
        )

        # System admin should be able to create high security roles
        await rbac_manager.create_role(
            role_dto=high_security_role_dto, request_from=get_security_admin
        )
        await uow.commit()

        # Get the created role
        high_role = await rbac_manager.get_role(
            role_name="high_level_role", request_from=get_security_admin
        )

        # Regular admin shouldn't be able to modify system roles
        system_role = await rbac_manager.get_role(
            role_name="super_admin", request_from=get_security_project_manager
        )

        system_role.description = "Attempted modification"
        high_role.description = "Attempted modification"

        with pytest.raises(AccessDeniedException):
            await rbac_manager.update_role(
                role=system_role, request_from=get_security_project_manager
            )

        with pytest.raises(AccessDeniedException):
            await rbac_manager.update_role(
                role=high_role, request_from=get_security_project_manager
            )


async def test_assign_already_assigned_role(
    di_container, get_security_admin, create_test_user
):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        user_reader: BaseUserReader = await c.get(BaseUserReader)

        user = await user_reader.get_user_by_email("test_email@test.com")

        # Get or create a role
        existing_role = await rbac_manager.get_role(
            role_name="user", request_from=get_security_admin
        )

        # Assign role first time
        user = await rbac_manager.assign_role_to_user(
            user=user, role=existing_role, request_from=get_security_admin
        )

        # Assign same role again (should be idempotent)
        user = await rbac_manager.assign_role_to_user(
            user=user, role=existing_role, request_from=get_security_admin
        )

        # Role should be in user's roles exactly once
        assert (
            sum(1 for r in user.roles if r.name.to_raw() == existing_role.name.to_raw())
            == 1
        )


async def test_remove_nonexistent_role(
    di_container, get_security_admin, create_test_user
):
    async with di_container() as c:
        rbac_manager: RBACManager = await c.get(RBACManager)
        user_reader: BaseUserReader = await c.get(BaseUserReader)

        user = await user_reader.get_user_by_email("test_email@test.com")

        # Get a role the user doesn't have
        role_dto = dto.RoleCreation(
            name="nonexistent_role",
            description="Role the user doesn't have",
            security_level=3,
            permissions=[],
        )

        role = await rbac_manager.create_role(
            role_dto=role_dto, request_from=get_security_admin
        )

        # Removing a role the user doesn't have should be idempotent
        updated_user = await rbac_manager.remove_role_from_user(
            user=user, role=role, request_from=get_security_admin
        )

        # User should remain unchanged
        assert role not in updated_user.roles
