from src.domain.base.exceptions.application import AppException
from dataclasses import dataclass


@dataclass(frozen=True)
class MessageBrokerException(AppException):

    @property
    def message(self) -> str:
        return "Message Broker Error"


@dataclass(frozen=True)
class MappingException(MessageBrokerException):
    event: str

    @property
    def message(self) -> str:
        return f"Mapping for event {self.event} failed"
