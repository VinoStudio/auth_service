from src.application.base.exception import ApplicationException
from dataclasses import dataclass


@dataclass(frozen=True)
class UsernameAlreadyExistsException(ApplicationException):
    @property
    def message(self):
        return f"Given username: {self.value!r} already exists"


@dataclass(frozen=True)
class EmailAlreadyExistsException(ApplicationException):
    @property
    def message(self):
        return f"Given email: {self.value!r} already taken"


@dataclass(frozen=True)
class PasswordIsInvalidException(ApplicationException):
    @property
    def message(self):
        return f"Password is invalid"


class UserNotFoundException(ApplicationException):
    @property
    def message(self):
        return f"User with {self.value} not found"


class PasswordTokenExpiredException(ApplicationException):

    @property
    def message(self):
        return f"Password token expired. Send reset password request again"
