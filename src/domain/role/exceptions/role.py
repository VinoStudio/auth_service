from dataclasses import dataclass

from src.domain.base.exceptions.domain import ValidationException


@dataclass(frozen=True)
class WrongRoleNameFormatException(ValidationException):
    value: str

    @property
    def message(self) -> str:
        return f"Given {self.value} has wrong format! Role name must be lowercase alphanumeric with underscores"
