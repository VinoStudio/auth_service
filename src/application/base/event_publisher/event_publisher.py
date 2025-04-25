from abc import (
    ABC,
    abstractmethod,
)
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Any, List, Type, Dict, List

from src.infrastructure.base.message_broker.producer import AsyncMessageProducer
from src.domain.base.events.base import BaseEvent
from src.application.base.events import (
    EventHandler,
)
from src.infrastructure.message_broker.events.internal.base import (
    IntegrationEvent,
    IntegrationEventType,
)


@dataclass(eq=False)
class BaseEventPublisher(ABC):
    _message_broker: AsyncMessageProducer
    event_map: Dict[IntegrationEventType, List[EventHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    @abstractmethod
    def register_event(
        self,
        event: IntegrationEventType,
        event_handlers: List[EventHandler[IntegrationEventType, Any]],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def handle_event(self, event: IntegrationEvent) -> None:
        raise NotImplementedError
