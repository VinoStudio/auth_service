from dataclasses import dataclass

from sqlalchemy import text

from src import domain
from src.infrastructure.base.repository import BaseUserWriter
from src.infrastructure.base.repository.base import SQLAlchemyRepository
from src.infrastructure.db import models
from src.infrastructure.repositories.converters import (
    DomainToOrmConverter,
)
from src.infrastructure.repositories.helpers import repository_exception_handler


@dataclass
class UserWriter(SQLAlchemyRepository, BaseUserWriter):
    @repository_exception_handler
    async def create_user(self, user: domain.User) -> None:
        """Inserts user and all connected roles, sessions and permissions"""
        user_model: models.User = DomainToOrmConverter.domain_to_user_model(user)

        self._session.add(user_model)
        await self._session.flush()

        await self.update_user(user)

    @repository_exception_handler
    async def update_user(self, user: domain.User) -> None:
        """Updates from aggregate user, means user and all connected roles, sessions and permissions will be updated"""
        user_model = DomainToOrmConverter.domain_to_active_user(user)

        await self._session.merge(user_model)

    @repository_exception_handler
    async def check_if_field_exists(self, field: str, value: str) -> bool:
        """Query to check if a user with the given field value exists.

        Args:
            field: Field to check (either "username" or "email")
            value: The value to check for
        """
        if field not in ("username", "email"):
            raise ValueError("Field must be either 'username' or 'email'")

        query = f"""
            SELECT EXISTS (
                SELECT 1
                FROM "user"
                WHERE {field} = :{field}
            )
        """  # noqa S608

        result = await self._session.execute(text(query), {field: value})
        return result.scalar()

    @repository_exception_handler
    async def check_user_has_permission(
        self, user_id: str, permission_name: str
    ) -> bool:
        """Check if a user has a specific permission through any of their roles."""
        query = text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM user_roles ur
                JOIN role_permissions rp ON ur.role_id = rp.role_id
                JOIN permission p ON rp.permission_id = p.id
                WHERE ur.user_id = :user_id AND p.name = :permission_name
            )
        """
        )

        result = await self._session.execute(
            query, {"user_id": user_id, "permission_name": permission_name}
        )
        return result.scalar()
