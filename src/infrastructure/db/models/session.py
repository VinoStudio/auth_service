from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, Boolean, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from src.infrastructure.db.models import TimedBaseModel, UserMixin


class UserSession(TimedBaseModel, UserMixin):
    _back_populates_field = "sessions"
    _unique_field: bool = False
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=str(uuid7()))
    user_agent: Mapped[str] = mapped_column(String(100))
    device_info: Mapped[bytes] = mapped_column(LargeBinary(500))
    device_id: Mapped[str] = mapped_column(String(120))
    last_activity: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC),
        server_default=func.now(),
        type_=TIMESTAMP(timezone=True),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
