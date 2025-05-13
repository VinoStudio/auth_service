from dataclasses import dataclass

from src.application.base.exception import (
    ApplicationException,
    ResourceExistsException,
    ResourceNotFoundException,
)


@dataclass(frozen=True)
class RBACException(ApplicationException):
    """Base exception for RBAC operations"""


@dataclass(frozen=True)
class RoleAlreadyExistsException(ResourceExistsException):
    """Raised when attempting to create a role that already exists"""

    value: str

    @property
    def message(self) -> str:
        return f"You're trying to create existing role {self.value}"


@dataclass(frozen=True)
class PermissionAlreadyExistsException(ResourceExistsException):
    """Raised when attempting to create a permission that already exists"""

    value: str

    @property
    def message(self) -> str:
        return f"You're trying to create existing permission {self.value}"


@dataclass(frozen=True)
class RoleNotFoundException(ResourceNotFoundException):
    """Raised when a role is not found"""

    value: str

    @property
    def message(self) -> str:
        return f"Role {self.value} not found"


@dataclass(frozen=True)
class PermissionNotFoundException(ResourceNotFoundException):
    """Raised when a permission is not found"""

    value: str

    @property
    def message(self) -> str:
        return f"Permission {self.value} not found"


@dataclass(frozen=True)
class UnauthorizedRBACOperationException(RBACException):
    """Raised when a user tries to perform an RBAC operation they're not authorized for"""

    value: str

    @property
    def message(self) -> str:
        return "You're not authorized to perform this operation"


@dataclass(frozen=True)
class RoleInUseException(RBACException):
    """Raises when trying to delete a role that is in use"""

    value: str

    @property
    def message(self) -> str:
        return self.value


@dataclass(frozen=True)
class PermissionInUseException(RBACException):
    """Raised when a user tries to delete a permission that is in use"""

    value: str

    @property
    def message(self) -> str:
        return self.value


@dataclass(frozen=True)
class AccessDeniedException(UnauthorizedRBACOperationException):
    """Raised when a user tries to perform an RBAC operation they're not have rights for"""

    value: str

    @property
    def message(self) -> str:
        return self.value


@dataclass(frozen=True)
class RoleCreationAccessDeniedException(UnauthorizedRBACOperationException):
    """Raised when a user tries to perform an RBAC operation they're not have rights for"""

    value: str

    @property
    def message(self) -> str:
        return "You cannot create role higher than yours"


@dataclass(frozen=True)
class ValidationException(RBACException):
    """Raises when given data is not valid"""

    value: str

    @property
    def message(self) -> str:
        return self.value
