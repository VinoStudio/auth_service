from src.infrastructure.base.exception import InfrastructureException
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseException(InfrastructureException):
    @property
    def message(self):
        return "Database Error occurred"


@dataclass(frozen=True)
class CommitErrorException(DatabaseException):
    pass


@dataclass(frozen=True)
class RollbackErrorException(DatabaseException):
    pass


@dataclass(frozen=True)
class RepositoryException(DatabaseException):
    pass
