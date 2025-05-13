import re
from dataclasses import dataclass

import bcrypt

from src.domain.base.values.base import ValueObject
from src.domain.user.exceptions import (
    WrongPasswordFormatException,
)

PASSWORD_PATTERN_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$")


@dataclass(frozen=True)
class Password(ValueObject):
    value: bytes

    def _validate(self) -> None: ...

    @classmethod
    def create(cls, password: str) -> "Password":
        if not PASSWORD_PATTERN_REGEX.match(password):
            raise WrongPasswordFormatException("")

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        return cls(value=hashed)

    def verify(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.value)

    def to_raw(self) -> bytes:
        return self.value
