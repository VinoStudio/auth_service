from dataclasses import dataclass

from src.application.base.exception import (
    ResourceExistsException,
    ResourceNotFoundException,
)


@dataclass(frozen=True)
class UsernameAlreadyExistsException(ResourceExistsException):
    @property
    def message(self) -> str:
        return f"Given username: {self.value!r} already exists"


@dataclass(frozen=True)
class EmailAlreadyExistsException(ResourceExistsException):
    @property
    def message(self) -> str:
        return f"Given email: {self.value!r} already taken"


@dataclass(frozen=True)
class PasswordIsInvalidException(ResourceExistsException):
    @property
    def message(self) -> str:
        return "Password is invalid"


class UserNotFoundException(ResourceNotFoundException):
    @property
    def message(self) -> str:
        return f"User with {self.value} not found"


class PasswordTokenExpiredException(ResourceNotFoundException):
    @property
    def message(self) -> str:
        return "Password token expired. Send reset password request again"


class EmailTokenExpiredException(ResourceNotFoundException):
    @property
    def message(self) -> str:
        return "Email token expired. Send reset password request again"


class OAuthConnectionTokenExpiredException(ResourceNotFoundException):
    @property
    def message(self) -> str:
        return "Account connection token expired. Send connection request again"
