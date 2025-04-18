from dataclasses import dataclass, field
from abc import ABC
from datetime import datetime, UTC

from uuid6 import uuid7


@dataclass
class BaseEntity(ABC):
    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        kw_only=True,
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(UTC), kw_only=True
    )
