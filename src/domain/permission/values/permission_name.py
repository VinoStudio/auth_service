import re
from dataclasses import dataclass

from src.domain.base.values.base import ValueObject
from src.domain.permission.exceptions import WrongPermissionNameFormatException

PERMISSION_NAME_PATTERN_REGEX = re.compile(r"^[a-z]{2,15}:[a-z][a-z0-9_]{3,30}$")


@dataclass(frozen=True)
class PermissionName(ValueObject[str]):
    value: str

    def _validate(self) -> None:
        if not re.match(PERMISSION_NAME_PATTERN_REGEX, self.value):
            raise WrongPermissionNameFormatException(self.value)

    def to_raw(self) -> str:
        return self.value
