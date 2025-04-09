from datetime import datetime, UTC

from infrastructure.message_broker.events.external.base import ExternalEvent
from dataclasses import dataclass, field


@dataclass(frozen=True)
class UserRegistered(ExternalEvent):
    user_id: str
    username: str
    first_name: str
    last_name: str
    middle_name: str
    created_at: float | datetime = field(default_factory=lambda: datetime.now(UTC))
