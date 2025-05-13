from dataclasses import dataclass

from src.domain.base.exceptions.domain import DomainException


@dataclass(frozen=True)
class UserIsDeletedException(DomainException):
    user_id: str

    @property
    def message(self) -> str:
        return (
            f"User with id {self.user_id} is deleted. You can reactivate your account."
        )


@dataclass(frozen=True)
class PasswordDoesNotMatchException(DomainException):
    value: str

    @property
    def message(self) -> str:
        return "Password does not match"
