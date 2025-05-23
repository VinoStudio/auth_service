from dataclasses import dataclass

from src.domain.base.exceptions.application import AppException


@dataclass(eq=False, frozen=True)
class DomainException(AppException):
    @property
    def message(self) -> str:
        return "You must've send a wrong value"


@dataclass(frozen=True)
class ValidationException(DomainException): ...
