from enum import Enum
from typing import Dict, List
import structlog
import uuid6

from src.application.dependency_injector.di import get_container
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.role.values.role_name import RoleName
from src.domain.permission.values.permission_name import PermissionName
from src.domain.user.values import Email, UserId, Password, Username

import src.infrastructure.db.models as models
import src.domain as domain
from src.infrastructure.base.repository import BaseUserWriter
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.uow import UnitOfWork
from src.domain.role.entity.role_catalog import SystemRoles

logger = structlog.getLogger(__name__)


async def seed_roles_and_permissions() -> None:
    """Seed the database with default roles and permissions on application startup."""
    container = get_container()
    try:
        async with container() as c:
            role_repo = await c.get(BaseRoleRepository)
            user_writer = await c.get(BaseUserWriter)
            uow = await c.get(UnitOfWork)

            super_role = await role_repo.check_role_exists("super_admin")
            if super_role:
                print("Roles already exist, skipping seed")
                return

            # Log that we're starting the seed process
            logger.info("Starting to seed roles and permissions...")

            for role in SystemRoles.get_all_roles():
                await role_repo.create_role(role=role)
                await uow.commit()
            logger.info("Roles and permissions seeded successfully!")

            if not super_role:
                super_role = await role_repo.get_role_by_name("super_admin")

            super_user = domain.User.create(
                user_id=UserId(str(uuid6.uuid7())),
                email=Email("admin@admin.com"),
                username=Username("super_admin"),
                password=Password.create("admin1SS"),
                role=super_role,
            )

            await user_writer.create_user(super_user)
            await uow.commit()

    except Exception as e:
        import traceback

        logger.error(f"ERROR seeding roles and permissions: {e}")
        logger.error(traceback.format_exc())
        # Re-raise to ensure lifespan setup fails visibly
        raise
