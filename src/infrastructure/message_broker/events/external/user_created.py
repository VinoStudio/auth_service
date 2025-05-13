from dataclasses import dataclass

from src.infrastructure.message_broker.events.external.base import ExternalEvent


@dataclass(frozen=True)
class UserCreated(ExternalEvent):
    user_id: str
    username: str
