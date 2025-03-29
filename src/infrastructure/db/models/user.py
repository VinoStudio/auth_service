from typing import List, TYPE_CHECKING

from src.infrastructure.db.models import BaseModel
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, LargeBinary
from sqlalchemy.sql import func, cast
from sqlalchemy.sql.elements import Null
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7
from datetime import datetime, UTC
import sqlalchemy as sa
import bcrypt

if TYPE_CHECKING:
    from src.infrastructure.db.models import (
        Role,
        UserRoles,
        UserSession,
    )


class User(BaseModel):
    id: Mapped[str] = mapped_column(primary_key=True, unique=True, default=str(uuid7()))
    username: Mapped[str | None] = mapped_column(String(64), unique=True)
    email: Mapped[str] = mapped_column(String(64), unique=True)
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary(60))
    jwt_data: Mapped[bytes | None] = mapped_column(LargeBinary(100))
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC),
        server_default=func.now(),
        type_=TIMESTAMP(timezone=True),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        default=None,
        server_default=Null(),
        type_=TIMESTAMP(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC),
        server_default=func.now(),
        type_=TIMESTAMP(timezone=True),
    )
    version: Mapped[int]
    sessions: Mapped[List["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    roles: Mapped[List["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )
