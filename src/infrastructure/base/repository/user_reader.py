from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src import domain
from src.application import dto

if TYPE_CHECKING:
    from src.infrastructure.repositories.pagination import Pagination


@dataclass
class BaseUserReader(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> domain.User:
        raise NotImplementedError

    @abstractmethod
    async def get_active_user_by_id(self, user_id: str) -> domain.User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_username(self, username: str) -> domain.User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_email(self, email: str) -> domain.User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_oauth_provider_and_id(
        self, provider: str, provider_user_id: str
    ) -> domain.User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_oauth_accounts(self, user_id: str) -> list[domain.OAuthAccount]:
        raise NotImplementedError

    @abstractmethod
    async def get_user_credentials_by_email(
        self, email_or_username: str
    ) -> dto.UserCredentials:
        raise NotImplementedError

    @abstractmethod
    async def get_user_credentials_by_oauth_provider(
        self, provider_name: str, provider_user_id: str
    ) -> dto.OAuthUserIdentity:
        raise NotImplementedError

    @abstractmethod
    async def get_all_users(self, pagination: "Pagination") -> list[domain.User]:
        raise NotImplementedError

    @abstractmethod
    async def check_field_exists(self, field_name: str, value: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def check_username_exists(self, username: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def check_email_exists(self, email: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_user_roles_by_user_id(
        self, user_id: str, pagination: "Pagination"
    ) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def get_user_permissions_by_user_id(
        self, user_id: str, pagination: "Pagination"
    ) -> set[str]:
        raise NotImplementedError
