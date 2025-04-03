from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Type
from collections import defaultdict

from src.application.base.event_publisher.event_dispatcher import BaseEventDispatcher
from src.application.base.events import (
    EventHandler,
    ET,
    ER,
)
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.domain.base.events.base import BaseEvent


@dataclass
class EventDispatcher(BaseEventDispatcher):
    """Dispatches events to appropriate handlers based on event type"""

    session_factory: async_sessionmaker
    _handlers: Dict[BaseEvent, List[ET]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def register_handler(
        self, event_type: str, handler_class: Type[EventHandler]
    ) -> None:
        """Register a handler for a specific event type"""
        self._handlers[event_type].append(handler_class)

    async def dispatch(self, event_data: dict) -> None:
        """Dispatch an event to all registered handlers"""
        event_type = event_data.get("type")
        handler_classes = self._handlers.get(event_type, [])

        # if not handler_classes:
        #     logging.warning(f"No handlers registered for event type: {event_type}")
        #     return

        async with self.session_factory() as session:
            for handler_class in handler_classes:
                # Create a fresh handler with a new session
                handler = handler_class(session)
                await handler.handle(event_data)
