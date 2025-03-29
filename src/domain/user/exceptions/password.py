from dataclasses import dataclass
from src.domain.base.exceptions.domain import ValidationException


@dataclass(frozen=True)
class WrongPasswordFormatException(ValidationException):
    @property
    def message(self) -> str:
        return f"Password has wrong format!"