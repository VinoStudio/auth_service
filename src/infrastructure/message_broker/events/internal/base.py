from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import ClassVar, TypeVar

from uuid6 import uuid7


@dataclass(frozen=True, kw_only=True)
class IntegrationEvent:
    event_id: str = field(default_factory=lambda: str(uuid7()))
    event_timestamp: datetime = field(
        default_factory=lambda: datetime.now(UTC).timestamp()
    )
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
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
