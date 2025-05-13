from abc import ABC
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from src.infrastructure.message_broker.events.external.base import ExternalEvent

ExternalEventType = TypeVar("ExternalEventType", bound=type(ExternalEvent))
ExternalEventResult = TypeVar("ExternalEventResult", bound=Any)


@dataclass(eq=False, frozen=True)
class ExternalEventHandler(ABC, Generic[ExternalEventType, ExternalEventResult]):
    def handle(self, event: ExternalEventType) -> ExternalEventResult:
        raise NotImplementedError
