from dataclasses import dataclass
from src.domain.base.exceptions.domain import ValidationException


@dataclass(frozen=True)
class WrongEmailFormatException(ValidationException):
    value: str

    @property
    def message(self) -> str:
        return f"Email {self.value} has wrong format!"
