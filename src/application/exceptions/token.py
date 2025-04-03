from dataclasses import dataclass
from src.application.base.exception import ApplicationException

@dataclass(frozen=True)
class TokenRevokedException(ApplicationException):
    value: str

    @property
    def message(self):
        return f"Given {self.value} refresh token was revoked"

@dataclass(frozen=True)
class TokenExpiredException(ApplicationException):
    value: str

    @property
    def message(self):
        return f"Given {self.value} refresh token expired. Please, login again"


@dataclass(frozen=True)
class TokenValidationError(ApplicationException):
    value: str

    def message(self):
        return f"Given token is invalid"
