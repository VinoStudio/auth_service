from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from src.infrastructure.db.models import BaseModel, TimedBaseModel

if TYPE_CHECKING:
    from src.infrastructure.db.models import Permission, User


class UserRoles(BaseModel):
    __tablename__ = "user_roles"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("user.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True,
        nullable=False,
    )
    role_id: Mapped[str] = mapped_column(
        ForeignKey("role.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True,
        nullable=False,
    )


class Role(TimedBaseModel):
    id: Mapped[str] = mapped_column(primary_key=True, unique=True, default=str(uuid7()))
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(256))
    security_level: Mapped[int] = mapped_column(
        nullable=False, default=8, server_default=text("8")
    )
    users: Mapped[list["User"]] = relationship(
        argument="User", secondary="user_roles", back_populates="roles"
    )
    permissions: Mapped[list["Permission"]] = relationship(
        argument="Permission", secondary="role_permissions", back_populates="roles"
    )
