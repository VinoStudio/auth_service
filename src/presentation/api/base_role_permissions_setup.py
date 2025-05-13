import structlog
import uuid6

from src import domain
from src.application.dependency_injector.di import get_container
from src.domain.role.entity.role_catalog import SystemRoles
from src.domain.user.values import Email, Password, UserId, Username
from src.infrastructure.base.repository import BaseUserWriter
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.base.uow import UnitOfWork

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
                logger.debug("Roles already exist, skipping seed")
                return

            # Log that we're starting the seed process
            logger.debug("Starting to seed roles and permissions...")

            for role in SystemRoles.get_all_roles():
                await role_repo.create_role(role=role)
                await uow.commit()
            logger.debug("Roles and permissions seeded successfully!")

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

        logger.error("ERROR seeding roles and permissions:", exception=e)
        logger.error(traceback.format_exc())
        raise
