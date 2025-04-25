import structlog
from dataclasses import dataclass, field
from typing import Iterable, Any, List, Dict

from collections import defaultdict

from src.application.base.event_publisher.event_publisher import BaseEventPublisher
from src.application.base.events.event_handler import EventHandler
from src.infrastructure.message_broker.events.internal.base import (
    IntegrationEvent,
    IntegrationEventType,
)

logger = structlog.getLogger(__name__)


@dataclass(eq=False)
class EventPublisher(BaseEventPublisher):
    event_map: Dict[IntegrationEventType, List[EventHandler]] = field(
        default_factory=lambda: defaultdict(list), kw_only=True
    )

    def register_event(
        self,
        event: IntegrationEventType,
        event_handlers: Iterable[EventHandler[IntegrationEventType, Any]],
    ) -> None:
        self.event_map[event].extend(event_handlers)

    async def handle_event(self, event: IntegrationEvent) -> None:
        event_handlers: Iterable[EventHandler] = self.event_map.get(event.__class__)
        for handler in event_handlers:
            message = await handler.handle(event=event)
            await self._message_broker.publish(**message)
            logger.info("Event published", event_type=event.__class__.__name__)
