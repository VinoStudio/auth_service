from dataclasses import dataclass

from src.application.base.exception import (
    ResourceNotFoundException,
)


@dataclass(frozen=True)
class CommandIsNotRegisteredException(ResourceNotFoundException):
    @property
    def message(self) -> str:
        return f'Command "{self.value}" is not registered!'


@dataclass(frozen=True)
class QueryIsNotRegisteredException(ResourceNotFoundException):
    @property
    def message(self) -> str:
        return f'Query "{self.value}" is not registered!'


@dataclass(frozen=True)
class EventIsNotRegisteredException(ResourceNotFoundException):
    @property
    def message(self) -> str:
        return f'Event "{self.value}" is not registered!'
