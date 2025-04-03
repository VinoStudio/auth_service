from dataclasses import dataclass, field
from datetime import datetime, UTC
from email.policy import default
from typing import ClassVar, Callable, Type, TypeVar

from uuid6 import uuid7


@dataclass(frozen=True, kw_only=True)
class IntegrationEvent:
    event_id: str = field(default_factory=lambda: str(uuid7()))
    event_timestamp: datetime = field(
        default_factory=lambda: datetime.now(UTC).timestamp()
    )
    topic: ClassVar[str]


EventType = TypeVar("EventType", bound=type[IntegrationEvent])


def integration_event(
    topic: str,
) -> Callable[[EventType], EventType]:
    def _integration_event(cls: EventType) -> EventType:
        # Set class variables
        cls.topic = topic
        return cls

    return _integration_event
