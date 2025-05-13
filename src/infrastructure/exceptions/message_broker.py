from dataclasses import dataclass

from src.infrastructure.base.exception import InfrastructureException


@dataclass(frozen=True)
class MessageBrokerException(InfrastructureException):
    pass


@dataclass(frozen=True)
class FailedToConsumeMessageException(MessageBrokerException):
    value: str

    @property
    def message(self) -> str:
        return self.value
