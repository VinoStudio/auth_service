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

from src.domain.base.events.base import BaseEvent


@dataclass
class BaseEventDispatcher(ABC):
    """Dispatches events to appropriate handlers based on event type"""

    session_factory: async_sessionmaker
    _handlers: Dict[BaseEvent, List[ET]] = field(
        default_factory=lambda: defaultdict(list)
    )

    @abstractmethod
    def register_handler(
        self, event_type: str, handler_class: Type[EventHandler]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def dispatch(self, event_data: dict) -> None:
        raise NotImplementedError
