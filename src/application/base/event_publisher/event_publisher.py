from abc import (
    ABC,
    abstractmethod,
)
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Any

from infrastructure.base.message_broker.producer import AsyncMessageProducer
from domain.base.events.base import BaseEvent
from application.base.events import (
    EventHandler,
    ET,
    ER,
)

# from logic.exceptions.events import EventIsNotRegisteredException


@dataclass(eq=False)
class EventPublisher(ABC):
    event_map: dict[BaseEvent, list[EventHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )
    _message_broker: AsyncMessageProducer

    @abstractmethod
    def register_event(
        self, event: BaseEvent, event_handlers: Iterable[EventHandler[BaseEvent, Any]]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def handle_event(self, events: Iterable[BaseEvent]) -> None:
        raise NotImplementedError
