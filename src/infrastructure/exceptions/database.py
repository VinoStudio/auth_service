from dataclasses import dataclass

from src.infrastructure.base.exception import InfrastructureException


@dataclass(frozen=True)
class DatabaseException(InfrastructureException):
    @property
    def message(self) -> str:
        return "Database Error occurred"


@dataclass(frozen=True)
class CommitException(DatabaseException):
    pass


@dataclass(frozen=True)
class RollbackException(DatabaseException):
    pass


@dataclass(frozen=True)
class RepositoryException(DatabaseException):
    pass
