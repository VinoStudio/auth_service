from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.base.entity.base import BaseEntity


@dataclass
class OAuthAccount(BaseEntity):
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OAuthAccount):
            return False
        return (
            self.provider == other.provider
            and self.provider_user_id == other.provider_user_id
        )

    def __hash__(self) -> int:
        return hash((self.provider, self.provider_user_id))
