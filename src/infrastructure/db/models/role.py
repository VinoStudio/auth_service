from src.infrastructure.db.models import UserMixin, BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, PrimaryKeyConstraint
from typing import TYPE_CHECKING
from uuid6 import uuid7

from src.infrastructure.db.models.permission import RolePermissions

if TYPE_CHECKING:
    from src.infrastructure.db.models import RolePermissions, User, Permission


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

    __table_args__ = (PrimaryKeyConstraint("user_id", "role_id"),)


class Role(BaseModel):
    id: Mapped[str] = mapped_column(primary_key=True, unique=True, default=str(uuid7()))
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    users: Mapped[list["User"]] = relationship(
        argument="User", secondary="user_roles", back_populates="roles"
    )
    permissions: Mapped[list["Permission"]] = relationship(
        argument="Permission", secondary="role_permissions", back_populates="roles"
    )
