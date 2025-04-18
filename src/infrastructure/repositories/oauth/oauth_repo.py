from typing import List
from sqlalchemy import select, text
from dataclasses import dataclass

from src.infrastructure.base.repository import SQLAlchemyRepository
from src.infrastructure.base.repository.session_repo import BaseSessionRepository
from src.infrastructure.exceptions import (
    OAuthAccountDoesNotExistException,
)
from src.infrastructure.repositories.converters import (
    OrmToDomainConverter,
    DomainToOrmConverter,
)

import src.domain as domain
import src.infrastructure.db.models as models


# BaseOAuthAccountRepository
@dataclass
class OAuthAccountRepository(SQLAlchemyRepository):
    async def create_oauth_account(self, oauth_account: domain.OAuthAccount) -> None:
        """Create a new OAuth account link"""

        oauth_account_model: models.OAuthAccount = (
            DomainToOrmConverter.domain_to_oauth_account(oauth_account)
        )

        self._session.add(oauth_account_model)
        await self._session.flush()

    async def update_oauth_account(self, oauth_account: domain.OAuthAccount) -> None:
        """Update an existing OAuth account link"""

        oauth_account_model: models.OAuthAccount = (
            DomainToOrmConverter.domain_to_oauth_account(oauth_account)
        )

        await self._session.merge(oauth_account_model)

    async def deactivate_user_oauth_account(
        self, provider: str, provider_user_id: str, user_id: str
    ) -> None:
        stmt = text(
            """
            UPDATE oauthaccount
            SET is_active = :is_active
            WHERE provider = :provider
            AND provider_user_id = :provider_user_id
            AND user_id = :user_id
            """
        )

        await self._session.execute(
            stmt,
            dict(
                provider=provider,
                provider_user_id=provider_user_id,
                user_id=user_id,
                is_active=False,
            ),
        )

    async def deactivate_oauth_account(
        self, provider: str, provider_user_id: str
    ) -> None:
        """Deactivate a user session"""

        stmt = text(
            """
            UPDATE oauthaccount
            SET is_active = :is_active
            WHERE provider = :provider
            AND provider_user_id = :provider_user_id
            """
        )

        await self._session.execute(
            stmt,
            dict(provider=provider, provider_user_id=provider_user_id, is_active=False),
        )

    async def activate_user_oauth_account(
        self, provider: str, provider_user_id: str, user_id: str
    ) -> None:
        stmt = text(
            """
            UPDATE oauthaccount
            SET is_active = :is_active
            WHERE provider = :provider
            AND provider_user_id = :provider_user_id
            AND user_id = :user_id
            """
        )

        await self._session.execute(
            stmt,
            dict(
                provider=provider,
                provider_user_id=provider_user_id,
                user_id=user_id,
                is_active=True,
            ),
        )

    async def get_by_provider_and_id(
        self, provider: str, provider_user_id: str
    ) -> domain.OAuthAccount:
        stmt = select(models.OAuthAccount).where(
            models.OAuthAccount.provider == provider,
            models.OAuthAccount.provider_user_id == provider_user_id,
        )
        result = await self._session.execute(stmt)
        oauth_account = result.scalars().one_or_none()

        if oauth_account is None:
            raise OAuthAccountDoesNotExistException(f"{provider}:{provider_user_id}")

        return OrmToDomainConverter.oauth_account_to_domain(oauth_account)

    async def get_user_oauth_accounts(self, user_id: str) -> List[domain.OAuthAccount]:

        stmt = select(models.OAuthAccount).where(models.OAuthAccount.user_id == user_id)
        result = await self._session.execute(stmt)
        oauth_accounts = result.scalars().all()

        return [
            OrmToDomainConverter.oauth_account_to_domain(account)
            for account in oauth_accounts
        ]

    async def check_if_oauth_account_exists(
        self, provider: str, provider_user_id: str
    ) -> bool:
        """Check if an OAuth account link exists"""
        query = """
            SELECT EXISTS (
                SELECT 1
                FROM oauthaccount
                WHERE provider = :provider AND provider_user_id = :provider_user_id
            )
            """
        result = await self._session.execute(
            text(query), {"provider": provider, "provider_user_id": provider_user_id}
        )
        return result.scalar()

    async def check_if_user_oauth_account_exists(
        self, provider: str, provider_user_id: str, user_id: str
    ) -> bool:
        """Check if an OAuth account link exists"""
        query = """
            SELECT EXISTS (
                SELECT 1
                FROM oauthaccount
                WHERE provider = :provider AND provider_user_id = :provider_user_id AND user_id = :user_id
            )
            """
        result = await self._session.execute(
            text(query),
            {
                "provider": provider,
                "provider_user_id": provider_user_id,
                "user_id": user_id,
            },
        )
        return result.scalar()
