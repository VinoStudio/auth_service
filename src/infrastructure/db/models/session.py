from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, func, TIMESTAMP, LargeBinary
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from src.infrastructure.db.models import BaseModel, TimedBaseModel
from src.infrastructure.db.models import UserMixin
from datetime import datetime, UTC
from uuid6 import uuid7


if TYPE_CHECKING:
    from src.infrastructure.db.models import User


class UserSession(TimedBaseModel, UserMixin):
    _back_populates_field = "sessions"
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
