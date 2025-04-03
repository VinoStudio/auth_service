from dataclasses import dataclass
from abc import ABC
from typing import Any, Generic, TypeVar
from src.domain.base.events.base import BaseEvent


ET = TypeVar("ET", bound=type(BaseEvent))
ER = TypeVar("ER", bound=Any)


@dataclass(eq=False, frozen=True)
class EventHandler(ABC, Generic[ET, ER]):
    broker_topic: str = None

    def handle(self, event: ET) -> ER:
        raise NotImplementedError
