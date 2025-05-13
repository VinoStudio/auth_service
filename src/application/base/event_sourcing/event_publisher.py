from abc import (
    ABC,
    abstractmethod,
)
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from src.application.base.events import (
    EventHandler,
)
from src.infrastructure.base.message_broker.producer import AsyncMessageProducer
from src.infrastructure.message_broker.events.internal.base import (
    IntegrationEvent,
    IntegrationEventType,
)


@dataclass(eq=False)
class BaseEventPublisher(ABC):
    _message_broker: AsyncMessageProducer
    event_map: dict[IntegrationEventType, list[EventHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    @abstractmethod
    def register_event(
        self,
        event: IntegrationEventType,
        event_handlers: list[EventHandler[IntegrationEventType, Any]],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def handle_event(self, event: IntegrationEvent) -> None:
        raise NotImplementedError
