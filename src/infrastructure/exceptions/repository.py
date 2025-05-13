from dataclasses import dataclass

from src.infrastructure.base.exception import InfrastructureException


@dataclass(frozen=True)
class RepositoryException(InfrastructureException):
    pass


@dataclass(frozen=True)
class UserDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f"A user with {self.value!r} does not exist"


@dataclass(frozen=True)
class OAuthUserDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f"A user with {self.value!r} does not exist"


@dataclass(frozen=True)
class OAuthAccountDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f"An account with {self.value!r} does not exist"


@dataclass(frozen=True)
class UserWithUsernameDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f"A user with {self.value!r} username does not exist"


@dataclass(frozen=True)
class UserWithEmailDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f"A user with {self.value!r} email does not exist"


@dataclass(frozen=True)
class UserIsDeletedException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f"A user with {self.value!r} user_id is deleted"


@dataclass(frozen=True)
class RoleDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f"A role with {self.value!r} name does not exist"


@dataclass(frozen=True)
class PermissionDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f"A permission with {self.value!r} name does not exist"
