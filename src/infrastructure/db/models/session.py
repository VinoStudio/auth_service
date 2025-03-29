from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from src.infrastructure.db.models import BaseModel
from src.infrastructure.db.models import UserMixin
from datetime import datetime, UTC
from uuid6 import uuid7


if TYPE_CHECKING:
    from src.infrastructure.db.models import User


class UserSession(BaseModel, UserMixin):
    _back_populates_field = "sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=str(uuid7()))
    user_agent: Mapped[str] = mapped_column(String(100))
    device_info: Mapped[str] = mapped_column(String(120))
    last_activity: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
