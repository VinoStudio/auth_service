from dataclasses import dataclass

from src.domain.base.exceptions.application import AppException


@dataclass(frozen=True)
class InfrastructureException(AppException):
    """Base infrastructure exception."""

    value: str | None

    @property
    def message(self) -> str:
        return "Infrastructure Error occurred"
