from dataclasses import dataclass
import re

from src.domain.base.values.base import ValueObject
from src.domain.permission.exceptions import WrongPermissionNameFormatException

PERMISSION_NAME_PATTERN_REGEX = re.compile(r"^[a-z][a-z0-9_]{2,30}$")


@dataclass(frozen=True)
class PermissionName(ValueObject):
    value: str

    def _validate(self):
        if not re.match(PERMISSION_NAME_PATTERN_REGEX, self.value):
            raise WrongPermissionNameFormatException(self.value)
