from dataclasses import dataclass

from src.application.base.exception import ResourceExistsException


@dataclass(frozen=True)
class OAuthAccountDoesNotExistException(ResourceExistsException):
    value: str

    @property
    def message(self) -> str:
        return f"An account with {self.value!r} does not exist"


@dataclass(frozen=True)
class OAuthAccountAlreadyDeactivatedException(ResourceExistsException):
    value: str

    @property
    def message(self) -> str:
        return f"An account with {self.value!r} is already deactivated"


@dataclass(frozen=True)
class OAuthAccountAlreadyAssociatedException(ResourceExistsException):
    value: str

    @property
    def message(self) -> str:
        return f"An account with {self.value!r} is already associated"
