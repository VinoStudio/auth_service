from dataclasses import dataclass

from src.application.base.exception import ApplicationException


@dataclass(frozen=True)
class AuthenticationException(ApplicationException):
    pass


@dataclass(frozen=True)
class AuthorizationException(ApplicationException):
    pass


@dataclass(frozen=True)
class AccessRejectedException(AuthenticationException):
    """Raised when a user tries to perform operation and does not sign in"""

    value: str

    @property
    def message(self) -> str:
        return self.value


@dataclass(frozen=True)
class TokenRevokedException(AuthorizationException):
    value: str

    @property
    def message(self) -> str:
        return "Given refresh token was revoked"


@dataclass(frozen=True)
class TokenExpiredException(AuthorizationException):
    value: str

    @property
    def message(self) -> str:
        return "Given refresh token expired. Please, login again"


@dataclass(frozen=True)
class TokenValidationError(AuthorizationException):
    value: str

    @property
    def message(self) -> str:
        return "Given token is invalid"


@dataclass(frozen=True)
class MappingProviderException(AuthorizationException):
    value: str

    @property
    def message(self) -> str:
        return f"Unknown OAuth provider: {self.value}"
