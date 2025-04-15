from src.application.base.exception import ApplicationException
from src.application.exceptions.mediator import (
    CommandIsNotRegisteredException,
    QueryIsNotRegisteredException,
    EventIsNotRegisteredException,
)
from src.application.exceptions.user import (
    UsernameAlreadyExistsException,
    EmailAlreadyExistsException,
    PasswordIsInvalidException,
)

from src.application.exceptions.rbac import (
    RBACException,
    UnauthorizedRBACOperationException,
    RoleNotFoundException,
    RoleAlreadyExistsException,
    RoleCreationAccessDeniedException,
    PermissionNotFoundException,
    RoleInUseException,
    AccessDeniedException,
    PermissionAlreadyExistsException,
    PermissionInUseException,
)

from src.application.exceptions.jwt import (
    AuthenticationException,
    AuthorizationException,
    AccessRejectedException,
    TokenExpiredException,
    TokenRevokedException,
    TokenValidationError,
)

__all__ = (
    "ApplicationException",
    "TokenExpiredException",
    "TokenRevokedException",
    "TokenValidationError",
    "CommandIsNotRegisteredException",
    "QueryIsNotRegisteredException",
    "EventIsNotRegisteredException",
    "UsernameAlreadyExistsException",
    "EmailAlreadyExistsException",
    "PasswordIsInvalidException",
    "RBACException",
    "UnauthorizedRBACOperationException",
    "RoleNotFoundException",
    "RoleAlreadyExistsException",
    "PermissionNotFoundException",
    "RoleCreationAccessDeniedException",
    "RoleInUseException",
    "AccessDeniedException",
    "PermissionAlreadyExistsException",
    "PermissionInUseException",
    "AuthenticationException",
    "AuthorizationException",
    "AccessRejectedException",
)
