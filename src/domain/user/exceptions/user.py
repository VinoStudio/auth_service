from dataclasses import dataclass
from src.domain.base.exceptions.domain import DomainException


@dataclass(frozen=True)
class UserIsDeletedException(DomainException):
    user_id: str

    @property
    def message(self):
        return (
            f"User with id {self.user_id} is deleted. You can reactivate your account."
        )


@dataclass(frozen=True)
class PasswordDoesNotMatchException(DomainException):
    @property
    def message(self):
        return "Password does not match"
