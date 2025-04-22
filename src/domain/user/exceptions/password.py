from dataclasses import dataclass
from src.domain.base.exceptions.domain import ValidationException


@dataclass(frozen=True)
class WrongPasswordFormatException(ValidationException):
    @property
    def message(self) -> str:
        return (
            f"Password has wrong format! "
            f"Make sure it contains at least one uppercase letter, one lowercase letter and one number "
            f"and is at least 8 characters long!"
        )
