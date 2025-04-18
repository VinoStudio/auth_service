from src.infrastructure.exceptions.repository import (
    UserIdAlreadyExistsErrorException,
    RepositoryException,
    UserDoesNotExistException,
    UserWithUsernameDoesNotExistException,
    UserWithEmailDoesNotExistException,
    UserIsDeletedException,
    RoleDoesNotExistException,
    PermissionDoesNotExistException,
    OAuthUserDoesNotExistException,
    OAuthAccountDoesNotExistException,
)
from src.infrastructure.exceptions.database import (
    DatabaseException,
    RollbackErrorException,
    CommitErrorException,
)

__all__ = (
    "DatabaseException",
    "RepositoryException",
    "RollbackErrorException",
    "CommitErrorException",
    "UserIdAlreadyExistsErrorException",
    "UserIsDeletedException",
    "UserDoesNotExistException",
    "UserWithUsernameDoesNotExistException",
    "UserWithEmailDoesNotExistException",
    "RoleDoesNotExistException",
    "PermissionDoesNotExistException",
    "OAuthUserDoesNotExistException",
    "OAuthAccountDoesNotExistException",
)
