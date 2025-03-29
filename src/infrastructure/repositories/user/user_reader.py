from typing import Iterable, Sequence, Set
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import text

from src.infrastructure.db.models import User
from src.infrastructure.exceptions.repository import (
    UserDoesNotExistException,
    UserWithUsernameDoesNotExistException,
    UserWithEmailDoesNotExistException,
    UserIsDeletedException,
)
from src.infrastructure.base.repository.base import SQLAlchemyRepository
from src.infrastructure.base.repository import BaseUserReader
from src.infrastructure.repositories.pagination import Pagination
from src.infrastructure.repositories.converters import OrmToDomainConverter
from sqlalchemy import text

import src.infrastructure.db.models as models
import src.domain as domain


class UserReader(SQLAlchemyRepository, BaseUserReader):
    async def get_user_by_id(self, user_id: str) -> models.User:
        stmt = self.get_user().where(models.User.id == user_id)

        result = await self._session.execute(stmt)
        user: models.User | None = result.scalars().one()

        if user is None:
            raise UserDoesNotExistException(user_id)

        return OrmToDomainConverter.user_to_domain(user)

    async def get_active_user_by_id(self, user_id: str) -> models.User:
        user: domain.User | None = await self.get_user_by_id(user_id)

        if user is None:
            raise UserDoesNotExistException(user_id)

        if user.deleted_at is not None:
            raise UserIsDeletedException(user_id)

        return user

    async def get_user_by_username(self, username: str) -> models.User:
        stmt = self.get_user().where(models.User.username == username)

        result = await self._session.execute(stmt)
        user: models.User | None = result.scalars().one()

        if user is None:
            raise UserWithUsernameDoesNotExistException(username)

        if user.deleted_at is not None:
            raise UserIsDeletedException(user.id)

        return OrmToDomainConverter.user_to_domain(user)

    async def get_user_by_email(self, email: str) -> models.User:
        stmt = self.get_user().where(models.User.email == email)

        result = await self._session.execute(stmt)
        user: models.User | None = result.scalars().one()

        if user is None:
            raise UserWithEmailDoesNotExistException(email)

        if user.deleted_at is not None:
            raise UserIsDeletedException(user.id)

        return user

    async def get_all_users(self, pagination: Pagination) -> Iterable[models.User]:
        stmt = self.get_user().limit(pagination.limit).offset(pagination.offset)

        result = await self._session.execute(stmt)

        return [*result.scalars().all()]

    async def get_all_usernames(self) -> Iterable[str]: ...

    async def get_user_roles_by_id(self, user_id: str) -> Sequence[models.Role]:
        stmt = self.get_user_roles().where(models.User.id == user_id)

        result = await self._session.execute(stmt)

        return [
            OrmToDomainConverter.role_to_domain(role) for role in result.scalars().all()
        ]

    async def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permission names that a user has through their roles."""
        query = text(
            """
            SELECT DISTINCT p.name
            FROM permission p
            JOIN role_permissions rp ON p.id = rp.permission_id
            JOIN user_roles ur ON rp.role_id = ur.role_id
            WHERE ur.user_id = :user_id
        """
        )

        result = await self._session.execute(query, {"user_id": user_id})
        return {row[0] for row in result}

    @staticmethod
    def get_user():
        """Returns a base query with standard eager loading options for users"""
        return select(models.User).options(
            selectinload(models.User.roles).selectinload(models.Role.permissions),
            selectinload(models.User.sessions),
        )

    @staticmethod
    def get_user_roles():
        """Returns a base query with standard eager loading options for user roles"""
        return select(models.Role).options(
            selectinload(models.User.roles).selectinload(models.Role.permissions),
        )
