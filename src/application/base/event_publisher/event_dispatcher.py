from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Type
from collections import defaultdict
from src.application.base.events import (
    EventHandler,
    ET,
    ER,
)

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.application.base.events.external_event_handler import ExternalEventHandler
from src.domain.base.events.base import BaseEvent
from src.infrastructure.message_broker.events.external.base import ExternalEvent


@dataclass
class BaseEventDispatcher(ABC):
    """Dispatches events to appropriate handlers based on event type"""

    _handlers: Dict[ExternalEvent, List[ExternalEventHandler]] = field(
        default_factory=lambda: defaultdict(list)
    )

    @abstractmethod
    def register_handler(
        self,
        event_type: type[ExternalEvent],
        handler_class: List[ExternalEventHandler],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def dispatch(self, event: ExternalEvent) -> None:
        raise NotImplementedError
