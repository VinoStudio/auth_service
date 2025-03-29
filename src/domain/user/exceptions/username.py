from dataclasses import dataclass
from src.domain.base.exceptions.domain import ValidationException


@dataclass(frozen=True)
class UsernameIsTooLongException(ValidationException):
    username: str | None

    @property
    def message(self) -> str:
        return f"Username {self.username} is too long!"


@dataclass(frozen=True)
class UsernameIsTooShortException(ValidationException):
    username: str | None

    @property
    def message(self) -> str:
        return f"Username {self.username} is too short or empty!"


@dataclass(frozen=True)
class WrongUsernameFormatException(ValidationException):
    username: str | None

    @property
    def message(self) -> str:
        return f"Username {self.username} has wrong format!"
