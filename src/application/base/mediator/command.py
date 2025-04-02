from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from application.base.commands import BaseCommand
from application.base.commands import CommandHandler, CT, CR


@dataclass(eq=False)
class CommandMediator(ABC):
    command_map: dict[BaseCommand, list[CommandHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    @abstractmethod
    def register_command(
        self, command: BaseCommand, command_handlers: Iterable[CommandHandler[CT, CR]]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def handle_command(self, command: CT) -> Iterable[CR]:
        raise NotImplementedError
