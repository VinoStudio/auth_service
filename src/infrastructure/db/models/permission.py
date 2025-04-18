from typing import TYPE_CHECKING

from src.infrastructure.db.models import BaseModel, UserMixin, TimedBaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, func, ForeignKey
from uuid6 import uuid7

if TYPE_CHECKING:
    from src.infrastructure.db.models import User
    from src.infrastructure.db.models import Role


class RolePermissions(BaseModel):

    __tablename__ = "role_permissions"

    role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("role.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True,
    )
    permission_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("permission.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True,
    )


class Permission(TimedBaseModel):
    _back_populates_field = "permission"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=str(uuid7()))
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="noload",
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)
