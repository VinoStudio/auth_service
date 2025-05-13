from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field

from src.application.base.commands import (
    BaseCommand,
    CommandHandler,
    CommandResult,
    CommandType,
)
from src.application.base.mediator.command import BaseCommandMediator
from src.application.exceptions.mediator import CommandIsNotRegisteredException


@dataclass(eq=False)
class CommandMediator(BaseCommandMediator):
    command_map: dict[CommandType, list[CommandHandler]] = field(
        default_factory=lambda: defaultdict(list), kw_only=True
    )

    def register_command(
        self, command: CommandType, command_handlers: Iterable[CommandHandler]
    ) -> None:
        self.command_map[command].extend(command_handlers)

    async def handle_command(self, command: CommandType) -> Iterable[CommandResult]:
        command_type: type(BaseCommand) = command.__class__

        command_handlers: Iterable[CommandHandler] = self.command_map.get(command_type)

        if not command_handlers:
            raise CommandIsNotRegisteredException(command_type)

        return [await c.handle(command) for c in command_handlers]
