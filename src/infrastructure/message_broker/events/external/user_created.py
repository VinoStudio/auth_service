from datetime import datetime, UTC

from src.infrastructure.message_broker.events.external.base import ExternalEvent
from dataclasses import dataclass, field


@dataclass(frozen=True)
class UserCreated(ExternalEvent):
    user_id: str
    username: str
