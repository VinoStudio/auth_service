from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from src.infrastructure.db.models import TimedBaseModel, UserMixin


class OAuthAccount(TimedBaseModel, UserMixin):
    _back_populates_field = "oauth_accounts"
    _unique_field: bool = False
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=str(uuid7()))
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_email: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_user_id",
            name="oauth_provider_id",
        ),
    )
