from abc import ABC
from copy import copy
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from src.domain.base.entity.base import BaseEntity
from src.domain.base.events.base import BaseEvent

ET = TypeVar("ET", bound=type(BaseEvent))


@dataclass
class AggregateRoot(BaseEntity, ABC, Generic[ET]):
    _events: list[ET] = field(default_factory=list, kw_only=True)

    def register_event(self, event: ET) -> None:
        self._events.append(event)

    def get_events(self) -> list[ET]:
        return self._events

    def pull_events(self) -> list[ET]:
        events = copy(self._events)
        self.clear_events()
        return events

    def clear_events(self) -> None:
        self._events.clear()
