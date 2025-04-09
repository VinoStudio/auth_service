from dataclasses import dataclass

from src.application.base.exception import ApplicationException


class AuthenticationException(ApplicationException):
    pass


@dataclass(frozen=True)
class AccessRejectedException(AuthenticationException):
    """Raised when a user tries to perform operation and does not sign in"""
    value: str

    def message(self):
        return self.value