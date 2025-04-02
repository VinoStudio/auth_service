from dataclasses import dataclass
from domain.base.exceptions.application import AppException


@dataclass(frozen=True)
class ApplicationException(AppException):
    value: str | None

    @property
    def message(self):
        return "Something went wrong on a server"
