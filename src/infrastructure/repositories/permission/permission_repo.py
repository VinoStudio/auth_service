from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from sqlalchemy import Select, select, text
from sqlalchemy.orm import selectinload

from src import domain
from src.infrastructure.base.repository import SQLAlchemyRepository
from src.infrastructure.base.repository.permission_repo import BasePermissionRepository
from src.infrastructure.db import models
from src.infrastructure.exceptions import PermissionDoesNotExistException
from src.infrastructure.repositories.converters import OrmToDomainConverter
from src.infrastructure.repositories.helpers import repository_exception_handler
from src.infrastructure.repositories.pagination import Pagination


@dataclass
class PermissionRepository(BasePermissionRepository, SQLAlchemyRepository):
    @repository_exception_handler
    async def create_permission(
        self, permission: domain.Permission
    ) -> models.Permission | None:
        permission_model = models.Permission(
            id=permission.id, name=permission.permission_name.to_raw()
        )
        self._session.add(permission_model)
        await self._session.flush()

    @repository_exception_handler
    async def delete_permission(self, permission_name: str) -> None:
        await self._session.execute(
            text("DELETE FROM permission WHERE name = :name"),
            {"name": permission_name},
        )

    @repository_exception_handler
    async def get_permission_by_id(
        self, permission_id: str
    ) -> domain.Permission | None:
        query = self.get_permission().where(models.Permission.id == permission_id)
        result = await self._session.execute(query)
        permission = result.scalars().one_or_none()

        if not permission:
            raise PermissionDoesNotExistException(permission_id)

        return OrmToDomainConverter.permission_to_domain(permission.id, permission.name)

    @repository_exception_handler
    async def get_permission_by_name(
        self, permission_name: str
    ) -> domain.Permission | None:
        query = self.get_permission().where(models.Permission.name == permission_name)
        result = await self._session.execute(query)
        permission = result.scalars().one_or_none()

        if not permission:
            raise PermissionDoesNotExistException(permission_name)

        return OrmToDomainConverter.permission_to_domain(permission.id, permission.name)

    @repository_exception_handler
    async def get_permission_roles(self, permission_id: str) -> list[domain.Role]:
        query = (
            select(models.Role)
            .options(selectinload(models.Role.permissions))
            .where(models.Permission.id == permission_id)
        )
        result = await self._session.execute(query)

        roles = result.scalars().all()
        return [OrmToDomainConverter.role_to_domain(role) for role in roles]

    @repository_exception_handler
    async def get_existing_permissions(self) -> Sequence[models.Permission]:
        query = self.get_permission()
        result = await self._session.execute(query)

        return result.scalars().all()

    @repository_exception_handler
    async def get_all_permissions(
        self, pagination: Pagination
    ) -> Iterable[domain.Permission]:
        query = self.get_permission().limit(pagination.limit).offset(pagination.offset)

        result = await self._session.execute(query)

        permissions = result.scalars().all()

        return [
            OrmToDomainConverter.permission_to_domain(permission.id, permission.name)
            for permission in permissions
        ]

    @repository_exception_handler
    async def check_permission_exists(self, permission_name: str) -> bool:
        query = text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM permission
                WHERE name = :permission_name
            )
        """
        )
        result = await self._session.execute(
            query, {"permission_name": permission_name}
        )
        return result.scalar()

    @repository_exception_handler
    async def count_roles_with_permission(self, permission_name: str) -> int:
        query = text(
            """
            SELECT COUNT(*)
            FROM role
            JOIN role_permissions ON role.id = role_permissions.role_id
            JOIN permission ON role_permissions.permission_id = permission.id
            WHERE permission.name = :permission_name
        """
        )
        result = await self._session.execute(
            query, {"permission_name": permission_name}
        )
        return result.scalar()

    @staticmethod
    def get_permission() -> Select:
        return select(models.Permission)
