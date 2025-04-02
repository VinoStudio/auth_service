from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from application.base.commands.base import BaseCommand

CT = TypeVar("CT", bound=type(BaseCommand))
CR = TypeVar("CR", bound=Any)


@dataclass(frozen=True)
class CommandHandler(ABC, Generic[CT, CR]):

    @abstractmethod
    async def handle(self, command: CT) -> CR: ...
