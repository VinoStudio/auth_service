from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.elements import Null
from uuid6 import uuid7

from src.infrastructure.db.models import TimedBaseModel

if TYPE_CHECKING:
    from src.infrastructure.db.models import (
        OAuthAccount,
        Role,
        UserSession,
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

    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )
