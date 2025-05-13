from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

if TYPE_CHECKING:
    from src.infrastructure.db.models import User


class UserMixin:
    _unique_field: bool = True
    _back_populates_field: str | None = None
    _nullable_field: bool = False

    @declared_attr
    def user_id(cls) -> Mapped[int]:  # noqa N805
        return mapped_column(
            ForeignKey("user.id"),
            unique=cls._unique_field,
            nullable=cls._nullable_field,
        )

    @declared_attr
    def user(cls) -> Mapped["User"]:  # noqa N805
        return relationship(argument="User", back_populates=cls._back_populates_field)
