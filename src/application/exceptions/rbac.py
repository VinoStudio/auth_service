from src.application.base.exception import ApplicationException
from dataclasses import dataclass


@dataclass(frozen=True)
class RBACException(ApplicationException):
    """Base exception for RBAC operations"""

    pass


@dataclass(frozen=True)
class RoleAlreadyExistsException(RBACException):
    """Raised when attempting to create a role that already exists"""

    value: str

    @property
    def message(self):
        return f"You're trying to create existing role {self.value}"


@dataclass(frozen=True)
class PermissionAlreadyExistsException(RBACException):
    """Raised when attempting to create a permission that already exists"""

    value: str

    @property
    def message(self):
        return f"You're trying to create existing permission {self.value}"


@dataclass(frozen=True)
class RoleNotFoundException(RBACException):
    """Raised when a role is not found"""

    value: str

    @property
    def message(self):
        return f"Role {self.value} not found"


@dataclass(frozen=True)
class PermissionNotFoundException(RBACException):
    """Raised when a permission is not found"""

    value: str

    @property
    def message(self):
        return f"Permission {self.value} not found"


@dataclass(frozen=True)
class UnauthorizedRBACOperationException(RBACException):
    """Raised when a user tries to perform an RBAC operation they're not authorized for"""

    value: str

    @property
    def message(self):
        return f"You're not authorized to perform this operation"


@dataclass(frozen=True)
class RoleInUseException(RBACException):
    """Raises when trying to delete a role that is in use"""

    value: str

    @property
    def message(self):
        return self.value


@dataclass(frozen=True)
class PermissionInUseException(RBACException):
    """Raised when a user tries to delete a permission that is in use"""

    value: str

    @property
    def message(self):
        return self.value


@dataclass(frozen=True)
class AccessDeniedException(UnauthorizedRBACOperationException):
    """Raised when a user tries to perform an RBAC operation they're not have rights for"""

    value: str

    @property
    def message(self):
        return self.value


@dataclass(frozen=True)
class RoleCreationAccessDeniedException(UnauthorizedRBACOperationException):
    """Raised when a user tries to perform an RBAC operation they're not have rights for"""

    value: str

    @property
    def message(self):
        return f"You cannot create role higher than yours"
