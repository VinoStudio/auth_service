from dataclasses import dataclass
from src.services.exception.base import ServiceException

@dataclass(frozen=True)
class TokenRevokedException(ServiceException):
    value: str

    @property
    def message(self):
        return f"Given {self.value} refresh token was revoked"

@dataclass(frozen=True)
class TokenExpiredException(ServiceException):
    value: str

    @property
    def message(self):
        return f"Given {self.value} refresh token expired. Please, login again"


@dataclass(frozen=True)
class TokenValidationError(ServiceException):
    value: str

    def message(self):
        return f"Given {self.value} is invalid"
