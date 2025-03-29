from dataclasses import dataclass
from src.infrastructure.db.models.user import User
from abc import ABC, abstractmethod
from typing import Iterable


@dataclass
class BaseUserReader(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_username(self, username: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_all_users(self, pagination: "Pagination") -> Iterable[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_usernames(self) -> Iterable[str]:
        raise NotImplementedError
