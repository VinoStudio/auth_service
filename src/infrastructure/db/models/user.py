from typing import List, TYPE_CHECKING

from src.infrastructure.db.models import BaseModel, TimedBaseModel
from sqlalchemy import String, TIMESTAMP, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.sql.elements import Null
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7
from datetime import datetime, UTC

if TYPE_CHECKING:
    from src.infrastructure.db.models import (
        Role,
        UserSession,
        OAuthAccount,
    )


class User(TimedBaseModel):
    id: Mapped[str] = mapped_column(primary_key=True, unique=True, default=str(uuid7()))
    username: Mapped[str | None] = mapped_column(String(64), unique=True)
    email: Mapped[str] = mapped_column(String(64), unique=True)
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary(120))
    jwt_data: Mapped[bytes | None] = mapped_column(LargeBinary(250))
    deleted_at: Mapped[datetime | None] = mapped_column(
        default=None,
        server_default=Null(),
        type_=TIMESTAMP(timezone=True),
        nullable=True,
    )
    version: Mapped[int]

    sessions: Mapped[List["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    oauth_accounts: Mapped[List["OAuthAccount"]] = relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    roles: Mapped[List["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )
