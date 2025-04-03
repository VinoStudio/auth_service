from datetime import timedelta, datetime, UTC
from dataclasses import dataclass, field
from uuid6 import uuid7

from src.domain.base.entity.base import BaseEntity
from src.domain.session.values.device_info import DeviceInfo


@dataclass
class Session(BaseEntity):
    id: str = field(default_factory=lambda: str(uuid7()), kw_only=True)
    user_id: str
    user_agent: str
    device_info: DeviceInfo
    device_id: str
    last_activity: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True

    def update_activity(self) -> None:
        """Record user activity, extending session life"""
        self.last_activity = datetime.now(UTC)

    def terminate(self) -> None:
        """End the session and return a domain event"""
        if not self.is_active:
            return None

        self.is_active = False

    def is_valid(self) -> bool:
        """Check if the session is valid for authentication"""
        return self.is_active

    def __eq__(self, other):
        if not isinstance(other, Session):
            return False
        return self.device_id == other.id

    def __hash__(self):
        return hash(self.device_id)
