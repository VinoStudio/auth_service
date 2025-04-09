from abc import (
    ABC,
    abstractmethod,
)
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Any

from src.infrastructure.base.message_broker.producer import AsyncMessageProducer
from src.domain.base.events.base import BaseEvent
from src.application.base.events import (
    EventHandler,
)
from src.infrastructure.message_broker.events.internal.base import IntegrationEvent


# from logic.exceptions.events import EventIsNotRegisteredException


@dataclass(eq=False)
class BaseEventPublisher(ABC):
    _message_broker: AsyncMessageProducer
    event_map: dict[IntegrationEvent, list[EventHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    @abstractmethod
    def register_event(
        self,
        event: IntegrationEvent,
        event_handlers: Iterable[EventHandler[BaseEvent, Any]],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def handle_event(self, event: IntegrationEvent) -> None:
        raise NotImplementedError
