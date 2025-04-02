from dataclasses import dataclass

from application.base.exception import ApplicationException


@dataclass(frozen=True)
class CommandIsNotRegisteredException(ApplicationException):

    @property
    def message(self):
        return f'Command "{self.value}" is not registered!'


@dataclass(frozen=True)
class QueryIsNotRegisteredException(ApplicationException):

    @property
    def message(self):
        return f'Query "{self.value}" is not registered!'


@dataclass(frozen=True)
class EventIsNotRegisteredException(ApplicationException):

    @property
    def message(self):
        return f'Event "{self.value}" is not registered!'
