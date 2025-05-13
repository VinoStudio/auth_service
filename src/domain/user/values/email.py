import re
from dataclasses import dataclass

from src.domain.base.values.base import ValueObject
from src.domain.user.exceptions import WrongEmailFormatException

EMAIL_PATTERN_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class Email(ValueObject):
    value: str

    def _validate(self) -> None:
        if not re.match(EMAIL_PATTERN_REGEX, self.value):
            raise WrongEmailFormatException(self.value)

    def to_raw(self) -> str:
        return self.value
