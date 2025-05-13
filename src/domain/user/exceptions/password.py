from dataclasses import dataclass

from src.domain.base.exceptions.domain import ValidationException


@dataclass(frozen=True)
class WrongPasswordFormatException(ValidationException):
    value: str

    @property
    def message(self) -> str:
        return (
            "Password has wrong format! "
            "Make sure it contains at least one uppercase letter, one lowercase letter and one number "
            "and is at least 8 characters long!"
        )
