from dataclasses import dataclass
from src.domain.base.values.base import ValueObject, VT
from src.domain.user.exceptions import (
    UsernameIsTooLongException,
    UsernameIsTooShortException,
    WrongUsernameFormatException,
)
import re

USERNAME_PATTERN_REGEX = re.compile(r"[A-Za-z][A-Za-z1-9_]+")


@dataclass(frozen=True)
class Username(ValueObject[str]):
    value: str

    def _validate(self) -> None:
        if not self.value:
            raise UsernameIsTooShortException(self.value)
        if len(self.value) > 24:
            raise UsernameIsTooLongException(self.value)
        if not USERNAME_PATTERN_REGEX.match(self.value):
            raise WrongUsernameFormatException(self.value)
