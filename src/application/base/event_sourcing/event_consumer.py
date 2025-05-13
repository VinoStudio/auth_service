from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field

from src.application.base.events.external_event_handler import (
    ExternalEventHandler,
    ExternalEventType,
)
from src.infrastructure.message_broker.events.external.base import ExternalEvent


@dataclass
class BaseEventConsumer(ABC):
    """Dispatches events to appropriate handlers based on event type"""

    _handlers: dict[ExternalEvent, list[ExternalEventHandler]] = field(
        default_factory=lambda: defaultdict(list)
    )

    @abstractmethod
    def register_handler(
        self,
        event_type: ExternalEventType,
        handler_class: list[ExternalEventHandler],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def handle(self, event: ExternalEvent) -> None:
        raise NotImplementedError
