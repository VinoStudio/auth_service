from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Generic, Type

from src.application.base.commands import BaseCommand
from src.application.base.commands import CommandHandler, CT, CR


@dataclass(eq=False)
class BaseCommandMediator(ABC):
    command_map: dict[CT, list[CommandHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    @abstractmethod
    def register_command(
        self,
        command: Type[BaseCommand],
        command_handlers: Iterable[CommandHandler[CT, CR]],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def handle_command(self, command: CT) -> Iterable[CR]:
        raise NotImplementedError
