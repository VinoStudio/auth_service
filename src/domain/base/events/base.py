from abc import ABC
from dataclasses import dataclass, field
from datetime import UTC, datetime

from uuid6 import uuid7


@dataclass(frozen=True)
class BaseEvent(ABC):
    id: str = field(default_factory=lambda: str(uuid7()), kw_only=True)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC), kw_only=True
    )
