from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Select, select, text
from sqlalchemy.orm import selectinload

from src import domain
from src.infrastructure.base.repository import SQLAlchemyRepository
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.db import models
from src.infrastructure.exceptions import RoleDoesNotExistException
from src.infrastructure.repositories.converters import (
    DomainToOrmConverter,
    OrmToDomainConverter,
)
from src.infrastructure.repositories.helpers import repository_exception_handler
from src.infrastructure.repositories.pagination import Pagination


@dataclass
class RoleRepository(SQLAlchemyRepository, BaseRoleRepository):
    @repository_exception_handler
    async def create_role(self, role: domain.Role) -> models.Role | None:
        """
        Since we use already existing permissions,
        we only create a new role and then update it with given domain.Role permissions
        """
        role_model: models.Role = DomainToOrmConverter.domain_to_role_creator(role)
        self._session.add(role_model)

        await self._session.flush()
        await self.update_role(role)

    @repository_exception_handler
    async def update_role(self, role: domain.Role) -> domain.Role | None:
        role_model: models.Role = DomainToOrmConverter.domain_to_role(role)

        await self._session.merge(role_model)

    @repository_exception_handler
    async def get_role_by_id(self, role_id: str) -> domain.Role | None:
        """Get a role with permissions by its ID."""
        query = self.get_role().where(models.Role.id == role_id)
        result = await self._session.execute(query)
        role = result.scalars().first()

        if not role:
            raise RoleDoesNotExistException(role_id)

        role_domain = OrmToDomainConverter.role_to_domain(role)

        return role_domain

    @repository_exception_handler
    async def get_role_by_name(self, name: str) -> domain.Role | None:
        query = self.get_role().where(models.Role.name == name)

        result = await self._session.execute(query)
        role = result.scalars().first()

        if not role:
            raise RoleDoesNotExistException(name)

        role_domain = OrmToDomainConverter.role_to_domain(role)

        return role_domain

    @repository_exception_handler
    async def get_all_roles(self, pagination: Pagination) -> Iterable[domain.Role]:
        query = self.get_role().limit(pagination.limit).offset(pagination.offset)

        result = await self._session.execute(query)

        roles = result.scalars().all()

        return [OrmToDomainConverter.role_to_domain(role) for role in roles]

    @repository_exception_handler
    async def update_role_name(self, role_id: str, name: str) -> models.Role | None:
        """Update a role's name."""
        await self._session.execute(
            text("UPDATE role SET name = :name WHERE id = :role_id"),
            {"name": name, "role_id": role_id},
        )

    @repository_exception_handler
    async def delete_role(self, role_id: str) -> bool:
        """Delete a role by its ID."""
        # Using raw SQL for direct deletion (more efficient)
        query = text(
            """
            DELETE FROM role
            WHERE id = :role_id
            RETURNING id
            """
        )

        result = await self._session.execute(query, {"role_id": role_id})

        return len(result.fetchall()) > 0

    @repository_exception_handler
    async def get_role_permissions(self, role_id: str) -> list[domain.Permission]:
        """Get all permissions for a specific role."""
        query = text(
            """
            SELECT p.id, p.name
            FROM permission p
            JOIN role_permissions rp ON p.id = rp.permission_id
            WHERE rp.role_id = :role_id
            ORDER BY p.name
        """
        )

        result = await self._session.execute(query, {"role_id": role_id})
        permissions = []
        for row in result:
            permission = OrmToDomainConverter.permission_to_domain(row[0], row[1])
            permissions.append(permission)
        return permissions

    @repository_exception_handler
    async def get_existing_roles(self) -> Sequence[models.Role]:
        query = select(models.Role)
        result = await self._session.execute(query)

        return result.scalars().all()

    # User-Role relationship methods
    @repository_exception_handler
    async def get_users_with_role(
        self,
        role_id: str,
        pagination: Pagination = Pagination(),
    ) -> list[dict[str, Any]]:
        """Get users who have a specific role with pagination."""
        query = text(
            """
            SELECT u.id, u.username
            FROM "user" u
            JOIN user_roles ur ON u.id = ur.user_id
            WHERE ur.role_id = :role_id
            ORDER BY u.username
            LIMIT :limit OFFSET :offset
        """
        )

        result = await self._session.execute(
            query,
            {
                "role_id": role_id,
                "limit": pagination.limit,
                "offset": pagination.offset,
            },
        )

        return [{"id": row[0], "username": row[1]} for row in result]

    @repository_exception_handler
    async def check_role_exists(self, role_name: str) -> bool:
        """Check if a role exists"""
        query = text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM role
                WHERE name = :role_name
            )
        """
        )
        result = await self._session.execute(query, {"role_name": role_name})
        return result.scalar()

    @repository_exception_handler
    async def count_users_with_role(self, role_name: str) -> int:
        query = text(
            """
            SELECT COUNT(*)
            FROM "user" u
            JOIN user_roles ur ON u.id = ur.user_id
            JOIN role r ON ur.role_id = r.id
            WHERE r.name = :role_name
        """
        )
        result = await self._session.execute(query, {"role_name": role_name})
        return result.scalar()

    @staticmethod
    def get_role() -> Select:
        return select(models.Role).options(selectinload(models.Role.permissions))

    @staticmethod
    def get_permission() -> Select:
        return select(models.Permission)
