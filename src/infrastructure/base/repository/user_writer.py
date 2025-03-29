from dataclasses import dataclass
from typing import Protocol
from abc import abstractmethod, ABC
import src.domain.user.entity.user as domain
import src.infrastructure.db.models.user as models


@dataclass
class BaseUserWriter(ABC):

    @abstractmethod
    async def create_user(self, user: domain.User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_user(self, user: domain.User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def check_if_username_exists(self, username: str) -> bool:
        raise NotImplementedError
