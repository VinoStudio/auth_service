from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.base.entity.base import BaseEntity
from src.domain.session.values.device_info import DeviceInfo


@dataclass(eq=False)
class Session(BaseEntity):
    user_id: str
    user_agent: str
    device_info: DeviceInfo
    device_id: str
    last_activity: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = field(default=True)

    def update_activity(self) -> None:
        """Record user activity, extending session life"""
        self.last_activity = datetime.now(UTC)

    def terminate(self) -> None:
        """End the session and return a domain event"""
        if not self.is_active:
            return

        self.is_active = False

    def is_valid(self) -> bool:
        """Check if the session is valid for authentication"""
        return self.is_active
