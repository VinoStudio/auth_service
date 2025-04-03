from typing import Optional, Dict, Any, List, Iterable, Sequence
from sqlalchemy.orm import selectinload
from sqlalchemy import select, text
from dataclasses import dataclass

from src.infrastructure.base.repository import SQLAlchemyRepository
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
from src.infrastructure.exceptions import RoleDoesNotExistException
from datetime import datetime, timedelta, UTC, timezone
import src.domain as domain
import src.infrastructure.db.models as models
from uuid6 import uuid7

from src.infrastructure.repositories.converters import (
    OrmToDomainConverter,
    DomainToOrmConverter,
)


@dataclass
class RoleRepository(SQLAlchemyRepository, BaseRoleRepository):

    async def create_role(self, role: domain.Role) -> Optional[models.Role]:
        """Since we use already existing permissions, we only create a new role and then update it with given domain.Role permissions"""

        role_model: models.Role = DomainToOrmConverter.domain_to_role_creator(role)
        self._session.add(role_model)

        await self._session.flush()
        await self.update_role(role)

    async def update_role(self, role: domain.Role) -> Optional[domain.Role]:
        role_model: models.Role = DomainToOrmConverter.domain_to_role(role)

        await self._session.merge(role_model)

    async def create_permission(
        self, permission: domain.Permission
    ) -> Optional[models.Permission]:
        """Create a new Permission from entity"""
        permission_model = models.Permission(
            id=permission.id, name=permission.permission_name.to_raw()
        )
        self._session.add(permission_model)
        await self._session.flush()

    async def get_role_by_id(self, role_id: str) -> Optional[domain.Role]:
        """Get a role with permissions by its ID."""

        query = self.get_role().where(models.Role.id == role_id)
        result = await self._session.execute(query)
        role = result.scalars().first()

        if not role:
            raise RoleDoesNotExistException(role_id)

        role_domain = OrmToDomainConverter.role_to_domain(role)

        return role_domain

    async def get_role_by_name(self, name: str) -> Optional[domain.Role]:
        query = self.get_role().where(models.Role.name == name)

        result = await self._session.execute(query)
        role = result.scalars().first()

        if not role:
            raise RoleDoesNotExistException(name)

        role_domain = OrmToDomainConverter.role_to_domain(role)

        return role_domain

    async def get_all_roles(self) -> Iterable[domain.Role]:
        query = self.get_role()

        result = await self._session.execute(query)

        roles = result.scalars().all()

        return [OrmToDomainConverter.role_to_domain(role) for role in roles]

    async def update_role_name(self, role_id: str, name: str) -> Optional[models.Role]:
        """Update a role's name."""

        await self._session.execute(
            text("UPDATE role SET name = :name WHERE id = :role_id"),
            {"name": name, "role_id": role_id},
        )

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

    # Role-Permission relationship methods

    async def set_role_permission(self, role_id: str, permission_id: str) -> None:
        """Add a permission to a role."""
        query = text(
            """
            INSERT INTO role_permissions (role_id, permission_id)
            VALUES (:role_id, :permission_id)
            ON CONFLICT (role_id, permission_id) DO NOTHING
            """
        )

        result = await self._session.execute(
            query, {"role_id": role_id, "permission_id": permission_id}
        )

    async def get_role_permissions(self, role_id: str) -> List[domain.Permission]:
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

    async def set_role_permissions(
        self, role_id: str, permission_ids: List[str]
    ) -> bool:
        """Set the exact permissions for a role (replacing existing ones)."""
        async with self._session.begin():
            # First clear existing permissions
            clear_query = text(
                """
                DELETE FROM role_permissions 
                WHERE role_id = :role_id
            """
            )

            await self._session.execute(clear_query, {"role_id": role_id})

            # Then add the new permissions if any
            if permission_ids:
                # Create values string for bulk insert
                values_params = []
                params = {"role_id": role_id}

                for i, perm_id in enumerate(permission_ids):
                    param_name = f"perm_id_{i}"
                    values_params.append(f"(:role_id, :{param_name})")
                    params[param_name] = perm_id

                values_clause = ", ".join(values_params)

                query = text(
                    f"""
                    INSERT INTO role_permissions (role_id, permission_id)
                    VALUES {values_clause}
                """
                )

                await self._session.execute(query, params)

        return True

    async def get_existing_permissions(self) -> Sequence[models.Permission]:
        query = self.get_permission()
        result = await self._session.execute(query)

        return result.scalars().all()

    async def get_existing_roles(self) -> Sequence[models.Role]:
        query = select(models.Role)
        result = await self._session.execute(query)

        return result.scalars().all()

    # User-Role relationship methods

    async def get_users_with_role(
        self, role_id: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
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
            query, {"role_id": role_id, "limit": limit, "offset": offset}
        )

        users = []
        for row in result:
            users.append({"id": row[0], "username": row[1]})
        return users

    # Analytics methods

    async def get_roles_with_metrics(self) -> List[Dict[str, Any]]:
        """Get all roles with counts of their permissions and users."""
        query = text(
            """
            SELECT r.id, r.name,
                (SELECT COUNT(*) FROM role_permissions WHERE role_id = r.id) as permission_count,
                (SELECT COUNT(*) FROM user_roles WHERE role_id = r.id) as user_count
            FROM role r
            ORDER BY r.name
            """
        )

        result = await self._session.execute(query)
        roles = []
        for row in result:
            roles.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "permission_count": row[2],
                    "user_count": row[3],
                }
            )
        return roles

    # Search methods

    # async def find_roles_by_name(self, name_fragment: str, limit: int = 20) -> List[Role]:
    #     """Find roles where the name contains the given fragment."""
    #     query = text(
    #         """
    #         SELECT id, name
    #         FROM role
    #         WHERE name ILIKE :name_pattern
    #         ORDER BY name
    #         LIMIT :limit
    #     """)
    #
    #     result = await self._session.execute(
    #         query,
    #         {"name_pattern": f"%{name_fragment}%", "limit": limit}
    #     )
    #
    #     roles = []
    #     for row in result:
    #         role = Role(id=row[0], name=row[1])
    #         roles.append(role)
    #     return roles

    @staticmethod
    def get_role():
        return select(models.Role).options(selectinload(models.Role.permissions))

    @staticmethod
    def get_permission():
        return select(models.Permission)
