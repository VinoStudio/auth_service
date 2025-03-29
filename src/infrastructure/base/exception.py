from dataclasses import dataclass

# from domain.base.exceptions.application import AppException


@dataclass(frozen=True)
class InfrastructureException(Exception):
    """Base infrastructure exception."""

    value: str | None

    @property
    def message(self):
        return "Infrastructure Error occurred"
