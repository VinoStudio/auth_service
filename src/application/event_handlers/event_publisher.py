from dataclasses import dataclass, field
from typing import Iterable, Any

from collections import defaultdict

from src.application.base.event_publisher.event_publisher import BaseEventPublisher
from src.application.base.events.event_handler import EventHandler, ET, ER
from src.domain.base.events.base import BaseEvent
from src.infrastructure.message_broker.events.base import IntegrationEvent


@dataclass(eq=False)
class EventPublisher(BaseEventPublisher):
    event_map: dict[IntegrationEvent, list[EventHandler]] = field(
        default_factory=lambda: defaultdict(list), kw_only=True
    )

    def register_event(
        self,
        event: IntegrationEvent,
        event_handlers: Iterable[EventHandler[IntegrationEvent, Any]],
    ) -> None:
        self.event_map[event].extend(event_handlers)

    async def handle_event(self, event: IntegrationEvent) -> None:
        event_handlers: Iterable[EventHandler] = self.event_map.get(event.__class__)
        for handler in event_handlers:
            message = await handler.handle(event=event)
            await self._message_broker.publish(**message)
