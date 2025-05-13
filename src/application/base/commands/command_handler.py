from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from src.application.base.commands.base import BaseCommand

CommandType = TypeVar("CommandType", bound=type(BaseCommand))
CommandResult = TypeVar("CommandResult", bound=Any)


@dataclass(frozen=True)
class CommandHandler(ABC, Generic[CommandType, CommandResult]):
    @abstractmethod
    async def handle(self, command: CommandType) -> CommandResult: ...
