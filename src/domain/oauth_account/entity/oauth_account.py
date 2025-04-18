from datetime import datetime, UTC
from dataclasses import dataclass, field
from uuid6 import uuid7

from src.domain.base.entity.base import BaseEntity


@dataclass
class OAuthAccount(BaseEntity):
    id: str = field(default_factory=lambda: str(uuid7()), kw_only=True)
    user_id: str
    provider: str
    provider_user_id: str
    provider_email: str
    is_active: bool = field(default=True)

    def update_provider_email(self, new_email: str) -> None:
        """Update the email address from the provider"""
        if self.provider_email != new_email:
            self.provider_email = new_email
            self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        """Deactivate this OAuth connection"""
        if self.is_active:
            self.is_active = False
            self.updated_at = datetime.now(UTC)

    def reactivate(self) -> None:
        """Reactivate this OAuth connection"""
        if not self.is_active:
            self.is_active = True
            self.updated_at = datetime.now(UTC)

    def is_valid(self) -> bool:
        """Check if the OAuth account link is valid"""
        return self.is_active

    def __eq__(self, other):
        if not isinstance(other, OAuthAccount):
            return False
        return (
            self.provider == other.provider
            and self.provider_user_id == other.provider_user_id
        )

    def __hash__(self):
        return hash((self.provider, self.provider_user_id))
