from dataclasses import dataclass, field
from src.infrastructure.message_broker.events.internal.base import (
    IntegrationEvent,
    integration_event,
)
from datetime import datetime, UTC


@dataclass(frozen=True)
@integration_event(topic="auth_service_topic")
class UserRegistered(IntegrationEvent):
    user_id: str
    username: str
    first_name: str
    last_name: str
    middle_name: str | None = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_type: str = field(default="UserRegistered")
