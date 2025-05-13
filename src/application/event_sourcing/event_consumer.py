from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field

import structlog

from src.application.base.event_sourcing.event_consumer import BaseEventConsumer
from src.application.base.events.external_event_handler import (
    ExternalEventHandler,
    ExternalEventResult,
    ExternalEventType,
)
from src.infrastructure.message_broker.events.external.base import ExternalEvent

logger = structlog.getLogger(__name__)


@dataclass
class EventConsumer(BaseEventConsumer):
    """Dispatches events to appropriate handlers based on event type"""

    _handlers: dict[ExternalEventType, list[ExternalEventHandler]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def register_handler(
        self, event_type: ExternalEventType, handlers: Iterable[ExternalEventHandler]
    ) -> None:
        """Register a handler for a specific event type"""
        self._handlers[event_type].extend(handlers)

    async def handle(self, event: ExternalEvent) -> ExternalEventResult:
        """Dispatch an event to all registered handlers"""
        event_handlers: Iterable[ExternalEventHandler] = self._handlers.get(
            event.__class__
        )

        for handler in event_handlers:
            await handler.handle(event=event)

        logger.info("Event handled by dispatcher", event_type=event.__class__.__name__)
