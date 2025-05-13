import re
from dataclasses import dataclass

from src.domain.base.values.base import ValueObject
from src.domain.role.exceptions.role import WrongRoleNameFormatException

ROLE_NAME_PATTER_REGEX = re.compile(r"^[a-z0-9_]{2,30}$")


@dataclass(frozen=True)
class RoleName(ValueObject):
    value: str

    def _validate(self) -> None:
        if not re.match(ROLE_NAME_PATTER_REGEX, self.value):
            raise WrongRoleNameFormatException(self.value)

    def to_raw(self) -> str:
        return self.value
