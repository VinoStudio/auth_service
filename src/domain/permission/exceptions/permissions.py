from dataclasses import dataclass

from src.domain.base.exceptions.domain import ValidationException


@dataclass(frozen=True)
class InvalidPermissionActionError(ValidationException):
    value: str

    @property
    def message(self) -> str:
        return f"'{self.value}' is not a valid permission action"


@dataclass(frozen=True)
class WrongPermissionNameFormatException(ValidationException):
    value: str

    @property
    def message(self) -> str:
        return f"Permission name {self.value} has wrong format!"
