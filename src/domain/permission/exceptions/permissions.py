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
        return (
            f"Permission name {self.value} has wrong format! "
            f"Permission name must be lowercase alphanumeric with underscore between resource and action. "
            f"Permission name length must be between 4 and 30 characters. "
            f"Like resource:action[0-9]"
        )
