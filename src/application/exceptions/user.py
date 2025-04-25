from src.application.base.exception import (
    ApplicationException,
    ResourceExistsException,
    ResourceNotFoundException,
)
from dataclasses import dataclass


@dataclass(frozen=True)
class UsernameAlreadyExistsException(ResourceExistsException):
    @property
    def message(self):
        return f"Given username: {self.value!r} already exists"


@dataclass(frozen=True)
class EmailAlreadyExistsException(ResourceExistsException):
    @property
    def message(self):
        return f"Given email: {self.value!r} already taken"


@dataclass(frozen=True)
class PasswordIsInvalidException(ResourceExistsException):
    @property
    def message(self):
        return f"Password is invalid"


class UserNotFoundException(ResourceNotFoundException):
    @property
    def message(self):
        return f"User with {self.value} not found"


class PasswordTokenExpiredException(ResourceNotFoundException):

    @property
    def message(self):
        return f"Password token expired. Send reset password request again"


class EmailTokenExpiredException(ResourceNotFoundException):

    @property
    def message(self):
        return f"Email token expired. Send reset password request again"


class OAuthConnectionTokenExpiredException(ResourceNotFoundException):

    @property
    def message(self):
        return f"Account connection token expired. Send connection request again"
