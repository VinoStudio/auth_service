from dataclasses import dataclass

from sqlalchemy import Select, text
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src import domain
from src.application import dto
from src.infrastructure.base.repository import BaseUserReader
from src.infrastructure.base.repository.base import SQLAlchemyRepository
from src.infrastructure.db import models
from src.infrastructure.exceptions.repository import (
    OAuthUserDoesNotExistException,
    UserDoesNotExistException,
    UserIsDeletedException,
    UserWithEmailDoesNotExistException,
    UserWithUsernameDoesNotExistException,
)
from src.infrastructure.repositories.converters import OrmToDomainConverter
from src.infrastructure.repositories.helpers import repository_exception_handler
from src.infrastructure.repositories.pagination import Pagination


@dataclass
class UserReader(SQLAlchemyRepository, BaseUserReader):
    @repository_exception_handler
    async def get_user_by_id(self, user_id: str) -> domain.User:
        stmt = self.get_user().where(models.User.id == user_id)

        result = await self._session.execute(stmt)
        user: models.User | None = result.scalars().one_or_none()

        if user is None:
            raise UserDoesNotExistException(user_id)

        return OrmToDomainConverter.user_to_domain(user)

    @repository_exception_handler
    async def get_active_user_by_id(self, user_id: str) -> domain.User:
        user: domain.User | None = await self.get_user_by_id(user_id)

        if user is None:
            raise UserDoesNotExistException(user_id)

        if user.deleted_at is not None:
            raise UserIsDeletedException(user_id)

        return OrmToDomainConverter.user_to_domain(user)

    @repository_exception_handler
    async def get_user_by_username(self, username: str) -> domain.User:
        stmt = self.get_user().where(models.User.username == username)

        result = await self._session.execute(stmt)
        user: models.User | None = result.scalars().one_or_none()

        if user is None:
            raise UserWithUsernameDoesNotExistException(username)

        if user.deleted_at is not None:
            raise UserIsDeletedException(user.id)

        return OrmToDomainConverter.user_to_domain(user)

    @repository_exception_handler
    async def get_user_by_email(self, email: str) -> domain.User:
        stmt = self.get_user().where(models.User.email == email)

        result = await self._session.execute(stmt)
        user: models.User | None = result.scalars().one_or_none()

        if user is None:
            raise UserWithEmailDoesNotExistException(email)

        if user.deleted_at is not None:
            raise UserIsDeletedException(user.id)

        return OrmToDomainConverter.user_to_domain(user)

    @repository_exception_handler
    async def get_user_by_oauth_provider_and_id(
        self, provider: str, provider_user_id: str
    ) -> domain.User:
        stmt = self.get_user().where(
            models.OAuthAccount.provider == provider,
            models.OAuthAccount.provider_user_id == provider_user_id,
            models.OAuthAccount.is_active,
        )

        result = await self._session.execute(stmt)
        user = result.scalars().one_or_none()

        if user is None:
            raise OAuthUserDoesNotExistException(
                f"provider: {provider} and id: {provider_user_id}"
            )

        return OrmToDomainConverter.user_to_domain(user)

    @repository_exception_handler
    async def get_user_oauth_accounts(self, user_id: str) -> list[domain.OAuthAccount]:
        stmt = select(models.OAuthAccount).where(
            models.OAuthAccount.user_id == user_id,
            models.OAuthAccount.is_active,
        )
        result = await self._session.execute(stmt)
        oauth_accounts = result.scalars().all()

        return [
            OrmToDomainConverter.oauth_account_to_domain(account)
            for account in oauth_accounts
        ]

    @repository_exception_handler
    async def get_user_credentials_by_email(self, email: str) -> dto.UserCredentials:
        result = await self._session.execute(
            text(
                """
                SELECT u.id, u.username, u.jwt_data, u.hashed_password
                FROM "user" u
                WHERE (u.email = :email) and u.deleted_at is null
                """
            ),
            {"email": email},
        )

        fetched_user = result.fetchone()

        if fetched_user is None:
            raise UserDoesNotExistException(email)

        return dto.UserCredentials(*fetched_user)

    @repository_exception_handler
    async def get_user_credentials_by_oauth_provider(
        self, provider_name: str, provider_user_id: str
    ) -> dto.OAuthUserIdentity:
        result = await self._session.execute(
            text(
                """
                SELECT u.id, u.jwt_data
                FROM "user" u
                JOIN oauthaccount oa ON u.id = oa.user_id
                WHERE oa.provider = :provider_name
                  AND oa.provider_user_id = :provider_user_id
                  AND u.deleted_at IS NULL
                  AND oa.is_active IS TRUE
                """
            ),
            {"provider_name": provider_name, "provider_user_id": provider_user_id},
        )

        fetched_user = result.fetchone()

        if fetched_user is None:
            raise OAuthUserDoesNotExistException(
                f"provider: {provider_name} and id: {provider_user_id}"
            )

        return dto.OAuthUserIdentity(
            *fetched_user,
            provider_user_id=provider_user_id,
            provider_name=provider_name,
        )

    @repository_exception_handler
    async def get_all_users(self, pagination: Pagination) -> list[domain.User]:
        stmt = self.get_user().limit(pagination.limit).offset(pagination.offset)

        result = await self._session.execute(stmt)

        return [
            OrmToDomainConverter.user_to_domain(user) for user in result.scalars().all()
        ]

    @repository_exception_handler
    async def check_field_exists(self, field_name: str, value: str) -> bool:
        if field_name not in ("username", "email"):
            raise ValueError("Field must be either 'username' or 'email'")

        result = await self._session.execute(
            text(
                f"""
                SELECT EXISTS (
                    SELECT 1
                    FROM "user"
                    WHERE {field_name} = :{field_name}
                )
                """  # noqa S608
            ),
            {field_name: value},
        )
        return result.scalar()

    @repository_exception_handler
    async def check_username_exists(self, username: str) -> bool:
        return await self.check_field_exists("username", username)

    @repository_exception_handler
    async def check_email_exists(self, email: str) -> bool:
        return await self.check_field_exists("email", email)

    @repository_exception_handler
    async def get_user_roles_by_user_id(
        self, user_id: str, pagination: Pagination
    ) -> list[str]:
        query = text(
            """
            SELECT r.name
            FROM role r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = :user_id
            ORDER BY r.security_level
            LIMIT :limit
            OFFSET :offset
            """
        )

        result = await self._session.execute(
            query,
            {
                "user_id": user_id,
                "limit": pagination.limit,
                "offset": pagination.offset,
            },
        )
        return [row[0] for row in result.fetchall()]

    @repository_exception_handler
    async def get_user_permissions_by_user_id(
        self, user_id: str, pagination: Pagination
    ) -> set[str]:
        """Get all permission names that a user has through their roles."""
        query = text(
            """
            SELECT DISTINCT p.name
            FROM permission p
            JOIN role_permissions rp ON p.id = rp.permission_id
            JOIN user_roles ur ON rp.role_id = ur.role_id
            WHERE ur.user_id = :user_id
            ORDER BY :order
            LIMIT :limit
            OFFSET :offset
        """
        )

        result = await self._session.execute(
            query,
            {
                "user_id": user_id,
                "limit": pagination.limit,
                "offset": pagination.offset,
                "order": pagination.order,
            },
        )
        return {row[0] for row in result}

    @staticmethod
    def get_user() -> Select:
        """Returns a base query with standard eager loading options for users"""
        return select(models.User).options(
            selectinload(models.User.roles).selectinload(models.Role.permissions),
            selectinload(models.User.sessions),
            selectinload(models.User.oauth_accounts),
        )

    @staticmethod
    def get_user_roles() -> Select:
        """Returns a base query with standard eager loading options for user roles"""
        return select(models.Role).options(
            selectinload(models.User.roles).selectinload(models.Role.permissions),
        )
