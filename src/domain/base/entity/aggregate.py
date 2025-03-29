from dataclasses import dataclass, field
from typing import Generic, TypeVar
from abc import ABC
from copy import copy

from src.domain.base.entity.base import BaseEntity
from src.domain.base.events.base import BaseEvent

ET = TypeVar("ET", bound=type(BaseEvent))


@dataclass
class AggregateRoot(BaseEntity, ABC, Generic[ET]):
    _events: list[ET] = field(default_factory=list, kw_only=True)

    def register_event(self, event: ET):
        self._events.append(event)

    def get_events(self) -> list[ET]:
        return self._events

    def pull_events(self):
        events = copy(self._events)
        self.clear_events()
        return events

    def clear_events(self):
        self._events.clear()
