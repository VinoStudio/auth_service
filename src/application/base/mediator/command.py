from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field

from src.application.base.commands import (
    BaseCommand,
    CommandHandler,
    CommandResult,
    CommandType,
)


@dataclass(eq=False)
class BaseCommandMediator(ABC):
    command_map: dict[CommandType, list[CommandHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    @abstractmethod
    def register_command(
        self,
        command: type[BaseCommand],
        command_handlers: Iterable[CommandHandler[CommandType, CommandResult]],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def handle_command(self, command: CommandType) -> Iterable[CommandResult]:
        raise NotImplementedError
