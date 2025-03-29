from datetime import timedelta, datetime, UTC
from dataclasses import dataclass, field

from src.domain.base.entity.base import BaseEntity


@dataclass
class Session(BaseEntity):
    id: str
    user_id: str
    device_info: str
    user_agent: str
    last_activity: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True

    def update_activity(self) -> None:
        """Record user activity, extending session life"""
        self.last_activity = datetime.now(UTC)

    def terminate(self, reason: str = "user_logout") -> None:
        """End the session and return a domain event"""
        if not self.is_active:
            return None

        self.is_active = False

    def is_valid(self) -> bool:
        """Check if the session is valid for authentication"""
        return self.is_active
