from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import ClassVar, Callable, Type, TypeVar

from uuid6 import uuid7


@dataclass(frozen=True, kw_only=True)
class IntegrationEvent:
    event_id: str = field(default_factory=lambda: str(uuid7()))
    event_timestamp: datetime = field(
        default_factory=lambda: datetime.now(UTC).timestamp()
    )
    topic: ClassVar[str]


IntegrationEventType = TypeVar("IntegrationEventType", bound=type[IntegrationEvent])


def integration_event(
    topic: str,
) -> Callable[[IntegrationEventType], IntegrationEventType]:
    def _integration_event(cls: IntegrationEventType) -> IntegrationEventType:
        # Set class variables
        cls.topic = topic
        return cls

    return _integration_event
