from dataclasses import dataclass
from abc import ABC
from typing import Any, Generic, TypeVar
from domain.base.events.base import BaseEvent

from infrastructure.message_broker.events import ExternalEvent

ET = TypeVar("ET", bound=type(ExternalEvent))
ER = TypeVar("ER", bound=Any)


@dataclass(eq=False)
class ExternalEventHandler(ABC, Generic[ET, ER]):
    def handle(self, event: ET) -> ER:
        raise NotImplementedError
