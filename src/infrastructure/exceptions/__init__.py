from src.infrastructure.exceptions.database import (
    CommitException,
    DatabaseException,
    RollbackException,
)
from src.infrastructure.exceptions.message_broker import (
    FailedToConsumeMessageException,
    MessageBrokerException,
)
from src.infrastructure.exceptions.repository import (
    OAuthAccountDoesNotExistException,
    OAuthUserDoesNotExistException,
    PermissionDoesNotExistException,
    RepositoryException,
    RoleDoesNotExistException,
    UserDoesNotExistException,
    UserIsDeletedException,
    UserWithEmailDoesNotExistException,
    UserWithUsernameDoesNotExistException,
)

__all__ = (
    "CommitException",
    "DatabaseException",
    "FailedToConsumeMessageException",
    "MessageBrokerException",
    "OAuthAccountDoesNotExistException",
    "OAuthUserDoesNotExistException",
    "PermissionDoesNotExistException",
    "RepositoryException",
    "RoleDoesNotExistException",
    "RollbackException",
    "UserDoesNotExistException",
    "UserIsDeletedException",
    "UserWithEmailDoesNotExistException",
    "UserWithUsernameDoesNotExistException",
)
