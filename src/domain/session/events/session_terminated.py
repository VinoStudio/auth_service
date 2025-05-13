from dataclasses import dataclass

from src.domain.base.events.base import BaseEvent


@dataclass(eq=False, frozen=True)
class SessionTerminatedEvent(BaseEvent):
    user_id: str | None
    session_id: str
    device_info: str
