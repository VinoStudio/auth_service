from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.infrastructure.message_broker.events.internal.base import (
    IntegrationEvent,
    integration_event,
)


@dataclass(frozen=True)
@integration_event(topic="auth_service_topic")
class UserRegistered(IntegrationEvent):
    user_id: str
    username: str
    first_name: str
    last_name: str
    middle_name: str | None = field(default=None)
    event_type: str = field(default="UserRegistered")
