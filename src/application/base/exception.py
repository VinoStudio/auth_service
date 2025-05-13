from dataclasses import dataclass

from src.domain.base.exceptions.application import AppException


@dataclass(frozen=True)
class ApplicationException(AppException):
    value: str | None

    @property
    def message(self) -> str:
        return "Something went wrong on a server"


@dataclass(frozen=True)
class ResourceNotFoundException(ApplicationException):
    """Base class for all 404 Not Found exceptions"""

    value: str


@dataclass(frozen=True)
class ResourceExistsException(ApplicationException):
    """Base class for all 409 Conflict exceptions"""

    value: str
