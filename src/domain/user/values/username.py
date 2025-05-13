import re
from dataclasses import dataclass

from src.domain.base.values.base import ValueObject
from src.domain.user.exceptions import (
    UsernameIsTooLongException,
    UsernameIsTooShortException,
    WrongUsernameFormatException,
)

USERNAME_PATTERN_REGEX = re.compile(r"[A-Za-z][A-Za-z1-9_]+")
MAX_USERNAME_SYMBOLS = 24


@dataclass(frozen=True)
class Username(ValueObject[str]):
    value: str

    def _validate(self) -> None:
        if not self.value:
            raise UsernameIsTooShortException(self.value)
        if len(self.value) > MAX_USERNAME_SYMBOLS:
            raise UsernameIsTooLongException(self.value)
        if not USERNAME_PATTERN_REGEX.match(self.value):
            raise WrongUsernameFormatException(self.value)

    def to_raw(self) -> str:
        return self.value
