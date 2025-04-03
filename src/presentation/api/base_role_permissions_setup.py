from enum import Enum
from typing import Dict, List

from src.application.dependency_injector.di import get_container
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.role.values.role_name import RoleName
from src.domain.permission.values.permission_name import PermissionName

import src.infrastructure.db.models as models
import src.domain as domain
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.uow import UnitOfWork


class Permission(Enum):
    # User management
    READ_USERS = domain.Permission(PermissionName("read:users"))
    CREATE_USERS = domain.Permission(PermissionName("create:users"))
    UPDATE_USERS = domain.Permission(PermissionName("update:users"))
    DELETE_USERS = domain.Permission(PermissionName("delete:users"))

    # Content/resource management
    READ_RESOURCES = domain.Permission(PermissionName("read:resources"))
    CREATE_RESOURCES = domain.Permission(PermissionName("create:resources"))
    UPDATE_RESOURCES = domain.Permission(PermissionName("update:resources"))
    DELETE_RESOURCES = domain.Permission(PermissionName("delete:resources"))

    # System configuration
    MANAGE_SETTINGS = domain.Permission(PermissionName("manage:settings"))
    VIEW_LOGS = domain.Permission(PermissionName("view:logs"))

    # Other common permissions
    ACCESS_API = domain.Permission(PermissionName("access:api"))
    GENERATE_REPORTS = domain.Permission(PermissionName("generate:reports"))


# Define basic roles with their associated permissions
ROLE_PERMISSIONS: Dict[str, List[Permission]] = {
    "admin": list(Permission),  # All permissions
    "user": [
        Permission.READ_RESOURCES,
        Permission.CREATE_RESOURCES,
        Permission.UPDATE_RESOURCES,
        Permission.DELETE_RESOURCES,
        Permission.ACCESS_API,
    ],
    "moderator": [
        Permission.READ_USERS,
        Permission.READ_RESOURCES,
        Permission.UPDATE_RESOURCES,
        Permission.DELETE_RESOURCES,
        Permission.VIEW_LOGS,
        Permission.ACCESS_API,
        Permission.GENERATE_REPORTS,
    ],
    "guest": [
        Permission.READ_RESOURCES,
        Permission.ACCESS_API,
    ],
    "service": [
        Permission.ACCESS_API,
        Permission.READ_RESOURCES,
        Permission.READ_USERS,
    ],
}


async def seed_roles_and_permissions() -> None:
    """Seed the database with default roles and permissions on application startup."""
    container = get_container()
    try:
        async with container() as c:
            role_repo = await c.get(BaseRoleRepository)
            uow = await c.get(UnitOfWork)

            # existing_roles = await role_repo._session.execute(select(models.Role))
            # if existing_roles.scalars().first():
            #     print("Roles already exist, skipping seed")
            #     return
            #
            # Log that we're starting the seed process
            print("Starting to seed roles and permissions...")

            for role_name, permissions in ROLE_PERMISSIONS.items():
                role = domain.Role(name=RoleName(role_name))
                for permission in permissions:
                    role.add_permission(permission.value)
                await role_repo.create_role(role=role)
                await uow.commit()
            print("Roles and permissions seeded successfully!")

    except Exception as e:
        import traceback

        print(f"ERROR seeding roles and permissions: {e}")
        print(traceback.format_exc())
        # Re-raise to ensure lifespan setup fails visibly
        raise
