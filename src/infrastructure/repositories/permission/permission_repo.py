from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Iterable, Sequence
from sqlalchemy.orm import selectinload
from sqlalchemy import select, text

from src.infrastructure.base.repository import SQLAlchemyRepository
from src.infrastructure.base.repository.permission_repo import BasePermissionRepository
import src.domain as domain
import src.infrastructure.db.models as models
from src.infrastructure.exceptions import PermissionDoesNotExistException
from src.infrastructure.repositories.converters import OrmToDomainConverter


@dataclass
class PermissionRepository(BasePermissionRepository, SQLAlchemyRepository):
    async def create_permission(
        self, permission: domain.Permission
    ) -> Optional[models.Permission]:
        """Create a new Permission from entity"""
        permission_model = models.Permission(
            id=permission.id, name=permission.permission_name.to_raw()
        )
        self._session.add(permission_model)
        await self._session.flush()

    async def delete_permission(self, permission_name: str) -> None:
        await self._session.execute(
            text("DELETE FROM permission WHERE name = :name"),
            {"name": permission_name},
        )

    async def get_permission_by_id(
        self, permission_id: str
    ) -> Optional[domain.Permission]:
        """Get a permission by its ID."""
        query = self.get_permission().where(models.Permission.id == permission_id)
        result = await self._session.execute(query)
        permission = result.scalars().one_or_none()

        if not permission:
            raise PermissionDoesNotExistException(permission_id)

        return OrmToDomainConverter.permission_to_domain(permission.id, permission.name)

    async def get_permission_by_name(
        self, permission_name: str
    ) -> Optional[domain.Permission]:
        """Get roles by name"""

        query = self.get_permission().where(models.Permission.name == permission_name)
        result = await self._session.execute(query)
        permission = result.scalars().one_or_none()

        if not permission:
            raise PermissionDoesNotExistException(permission_name)

        return OrmToDomainConverter.permission_to_domain(permission.id, permission.name)

    async def get_permission_roles(self, permission_id: str) -> List[domain.Role]:
        query = (
            select(models.Role)
            .options(selectinload(models.Role.permissions))
            .where(models.Permission.id == permission_id)
        )
        result = await self._session.execute(query)

        roles = result.scalars().all()
        return [OrmToDomainConverter.role_to_domain(role) for role in roles]

    async def get_existing_permissions(self) -> Sequence[models.Permission]:
        query = self.get_permission()
        result = await self._session.execute(query)

        return result.scalars().all()

    async def get_all_permissions(self) -> Iterable[domain.Permission]:
        query = self.get_permission()

        result = await self._session.execute(query)

        permissions = result.scalars().all()

        return [
            OrmToDomainConverter.permission_to_domain(permission.id, permission.name)
            for permission in permissions
        ]

    async def check_permission_exists(self, permission_name: str) -> bool:
        """Check if a role exists"""
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
    def get_permission():
        return select(models.Permission)
