from src.infrastructure.base.exception import InfrastructureException
from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryException(InfrastructureException):
    pass


@dataclass(frozen=True)
class UserIdAlreadyExistsErrorException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f'A user with the "{self.value}" user_id already exists'


@dataclass(frozen=True)
class UserDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f'A user with "{self.value}" user_id does not exist'


@dataclass(frozen=True)
class OAuthUserDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f'A user with "{self.value}" does not exist'


@dataclass(frozen=True)
class OAuthAccountDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f'An account with "{self.value}" does not exist'


@dataclass(frozen=True)
class UserWithUsernameDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f'A user with "{self.value}" username does not exist'


@dataclass(frozen=True)
class UserWithEmailDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f'A user with "{self.value}" email does not exist'


@dataclass(frozen=True)
class UserIsDeletedException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f'A user with "{self.value}" user_id is deleted'


@dataclass(frozen=True)
class RoleDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f"A role with '{self.value}' name does not exist"


@dataclass(frozen=True)
class PermissionDoesNotExistException(RepositoryException):
    value: str

    @property
    def message(self) -> str:
        return f"A permission with '{self.value}' name does not exist"
