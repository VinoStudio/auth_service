from typing import Iterable, Optional
from dataclasses import dataclass
from src.infrastructure.exceptions.repository import (
    UserDoesNotExistException,
    UserWithUsernameDoesNotExistException,
)
from src.infrastructure.base.repository.base import SQLAlchemyRepository
from src.infrastructure.base.repository import BaseUserWriter
from src.infrastructure.repositories.pagination import Pagination
from sqlalchemy import text
from src.infrastructure.repositories.converters import (
    OrmToDomainConverter,
    DomainToOrmConverter,
)
from uuid6 import uuid7
import src.domain as domain
import src.infrastructure.db.models as models


@dataclass
class UserWriter(SQLAlchemyRepository, BaseUserWriter):
    async def create_user(self, user: domain.User) -> None:
        """Only create user in DB, but role should add separately through set_user_basic_roles method"""

        user_model: models.User = DomainToOrmConverter.domain_to_user_model(user)

        self._session.add(user_model)
        await self._session.flush()

        await self.update_user(user)

    async def update_user(self, user: domain.User) -> None:
        """Updates from aggregate user, means user and all connected roles, sessions and permissions will be updated"""
        user_model = DomainToOrmConverter.domain_to_active_user(user)

        await self._session.merge(user_model)

    async def set_user_basic_roles(
        self, user_id: str, role: Optional[Iterable[domain.Role] | domain.Role] = None
    ) -> None:
        """Helper to add basic roles to user"""

        basic_roles = []
        query = text(
            """
            INSERT INTO user_roles (user_id, role_id)
            VALUES (:user_id, :role_id)
            """
        )

        if isinstance(role, Iterable):
            values = [{"user_id": user_id, "role_id": r.id} for r in role]
        else:
            values = {"user_id": user_id, "role_id": role.id}

        await self._session.execute(query, values)

    async def check_if_username_exists(self, username: str) -> bool:
        """Query to check if a user with the given username exists before inserting in DB."""

        result = await self._session.execute(
            text(
                """
                    SELECT EXISTS (
                        SELECT 1
                        FROM "user"
                        WHERE username = :username
                    )
                """
            ),
            dict(username=username),
        )
        # Extract the actual boolean value from the result
        return result.scalar()

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
