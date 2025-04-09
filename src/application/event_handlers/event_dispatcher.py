import structlog
from dataclasses import dataclass, field
from typing import Dict, List, Iterable
from collections import defaultdict

from src.application.base.event_publisher.event_dispatcher import BaseEventDispatcher
from src.application.base.events import (
    ET,
)
from src.application.base.events.external_event_handler import ExternalEventHandler
from src.domain.base.events.base import BaseEvent
from src.infrastructure.message_broker.events.external.base import ExternalEvent

logger = structlog.getLogger(__name__)


@dataclass
class EventDispatcher(BaseEventDispatcher):
    """Dispatches events to appropriate handlers based on event type"""

    _handlers: Dict[ExternalEvent, List[ET]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def register_handler(
        self, event_type: ExternalEvent, handlers: Iterable[ET]
    ) -> None:
        """Register a handler for a specific event type"""
        self._handlers[event_type].extend(handlers)

    async def dispatch(self, event: ExternalEvent) -> None:
        """Dispatch an event to all registered handlers"""
        event_handlers: Iterable[ExternalEventHandler] = self._handlers.get(
            event.__class__
        )

        for handler in event_handlers:
            await handler.handle(event=event)

        logger.info("Event handled by dispatcher", event_type=event.__class__.__name__)
