from enum import Enum

from src.domain.permission.exceptions.permissions import InvalidPermissionActionError


class PermissionAction(Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

    @classmethod
    def from_string(cls, action_str: str):
        try:
            return cls(action_str.lower())
        except (KeyError, ValueError):
            raise InvalidPermissionActionError(value=action_str)
