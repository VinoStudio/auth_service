from application.base.exception import ApplicationException
from dataclasses import dataclass


@dataclass(frozen=True)
class UsernameAlreadyExistsException(ApplicationException):
    @property
    def message(self):
        return f"Given username: {self.value!r} already exists"
