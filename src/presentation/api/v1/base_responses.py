import structlog
from litestar.openapi.spec import Example
from litestar.openapi.datastructures import ResponseSpec
from typing import Type, List, Any, Dict, Optional, Tuple, Iterable

import inspect
import litestar.status_codes as status
import re

from src.application.base.exception import ApplicationException
from src.application.exceptions import (
    TokenValidationError,
    TokenExpiredException,
    TokenRevokedException,
    AccessRejectedException,
    ValidationException,
    AccessDeniedException,
)
from src.domain.base.exceptions.application import AppException
from src.domain.permission.exceptions import WrongPermissionNameFormatException
from src.domain.role.exceptions.role import WrongRoleNameFormatException
from src.infrastructure.base.exception import InfrastructureException
from src.infrastructure.exceptions import (
    RoleDoesNotExistException,
    PermissionDoesNotExistException,
    UserDoesNotExistException,
    UserIsDeletedException,
    DatabaseException,
)
from src.presentation.api.exception_configuration import ErrorResponse

logger = structlog.getLogger(__name__)


class ExampleGenerator:
    """
    Utility for generating OpenAPI examples from exception classes.

    This generator handles various exception patterns:
    - Dataclass exceptions with different parameter names
    - Different inheritance hierarchies
    - Exceptions relying on parent class attributes
    - Various message formatting patterns
    """

    @staticmethod
    def _get_param_info(exception_class: Type[Any]) -> Dict[str, Any]:
        """Get parameter info from the class and its bases."""
        param_info = {"name": None, "required": False}

        # Check the exception class and its parent classes
        classes_to_check = [exception_class] + list(exception_class.__mro__[1:])

        for cls in classes_to_check:
            if hasattr(cls, "__annotations__"):
                # Check dataclass field annotations
                for name, _ in cls.__annotations__.items():
                    if name != "message" and name != "return":  # Skip methods
                        param_info["name"] = name
                        param_info["required"] = True
                        return param_info

            # Check constructor params if it's not a standard dataclass
            try:
                sig = inspect.signature(cls.__init__)
                params = list(sig.parameters.keys())[1:]  # Skip 'self'
                if params:
                    param_info["name"] = params[0]
                    param_info["required"] = True
                    return param_info
            except (ValueError, IndexError):
                continue

        return param_info

    @staticmethod
    def _get_sample_value(
        exception_class: Type[Any], param_name: Optional[str] = None
    ) -> Any:
        """Generate appropriate sample value based on exception class and parameter name."""
        name = exception_class.__name__

        # No parameters needed for some exceptions
        if param_name is None:
            return None

        # Special cases based on specific exception classes
        special_cases = {
            "RoleInUseException": "Role 'admin' is assigned to 5 users and cannot be deleted",
            "PermissionInUseException": "Permission 'users:write' is assigned to 3 roles and cannot be deleted",
            "AccessDeniedException": "You do not have the required permissions for this operation",
            "AccessRejectedException": "You must be signed in to perform this operation",
            "RoleCreationAccessDeniedException": "You cannot create a role with higher privileges than your current role",
            "TokenRevokedException": "The refresh token has been revoked",
            "TokenExpiredException": "Your authentication token has expired",
            "WrongPasswordFormatException": "Password format is invalid",
            "PasswordIsInvalidException": "The provided password is incorrect",
            "PasswordTokenExpiredException": "Password reset token has expired",
            "EmailTokenExpiredException": "Email verification token has expired",
            "AppException": "Something went wrong on server",
        }

        if name in special_cases:
            return special_cases[name]

        # Map exception types to appropriate sample values
        type_mappings = {
            "Command": "CreateUserCommand",
            "Query": "GetUserByIdQuery",
            "Event": "UserCreatedEvent",
            "UserId": "user_123",
            "Username": "john_doe",
            "Email": "user@example.com",
            "Password": "P@ssw0rd123",
            "Role": "example_role",
            "Permission": "resource:write",
            "Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "Provider": "google",
            "OAuth": "oauth_account_id",
            "Validation": "Invalid input data",
        }

        # Check for matches in the exception name
        for key, value in type_mappings.items():
            if key in name:
                return value

        # Check param name if no match in exception name
        param_mappings = {
            "user_id": "user_123",
            "username": "john_doe",
            "email": "user@example.com",
            "value": "sample_value",  # Generic fallback for "value"
        }

        if param_name in param_mappings:
            return param_mappings[param_name]

        # If the param is "value", try to infer from class name
        if param_name == "value":
            for key, value in type_mappings.items():
                if key in name:
                    return value

        # Default fallback
        return f"sample_{param_name}"

    @staticmethod
    def _detect_status_code(exception_class: Type[Any]) -> int:
        """Detect appropriate status code based on exception class name and hierarchy."""
        name = exception_class.__name__
        bases = [cls.__name__ for cls in exception_class.__mro__]

        # Direct status code mappings by exception name or base class
        if (
            any(term in name for term in ["NotFound", "DoesNotExist"])
            or "ResourceNotFoundException" in bases
        ):
            return 404
        elif (
            any(term in name for term in ["AlreadyExists", "InUse"])
            or "ResourceExistsException" in bases
        ):
            return 409
        elif (
            "Unauthorized" in name or "AccessDenied" in name or "RBACException" in bases
        ):
            return 403
        elif "Validation" in name or "WrongFormat" in name or "Invalid" in name:
            return 400
        elif "Authentication" in name or "Token" in name:
            if "Expired" in name or "Revoked" in name:
                return 401
            elif "Validation" in name:
                return 401
            elif "RBAC" in name:
                return 403

        # Default fallback
        return 500

    @staticmethod
    def _create_example_instance(
        exception_class: Type[Any],
    ) -> Tuple[Optional[Any], Optional[str]]:
        """Create an instance of the exception with appropriate sample data.
        Returns a tuple of (instance, error_message) where error_message is None if successful.
        """
        param_info = ExampleGenerator._get_param_info(exception_class)
        param_name = param_info["name"]

        if not param_info["required"]:
            try:
                return exception_class(), None
            except Exception as e:
                return None, str(e)

        sample_value = ExampleGenerator._get_sample_value(exception_class, param_name)

        try:
            if param_name:
                return exception_class(**{param_name: sample_value}), None
            else:
                return exception_class(), None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def _create_examples(
        exception_classes: Type[Any] | Iterable[Type[Any]], status_code: int
    ) -> List[Example]:
        """Internal method to generate examples with specified status code."""
        if not isinstance(exception_classes, tuple):
            exception_classes = exception_classes

        examples = []

        for exception_class in exception_classes:
            # Extract name and create readable format
            name = exception_class.__name__
            readable_name = " ".join(re.findall("[A-Z][^A-Z]*", name))

            # Get docstring if available
            description = readable_name

            # Create instance of the exception
            sample_exception, error = ExampleGenerator._create_example_instance(
                exception_class
            )

            # Create the example value structure
            value = {"status_code": status_code, "error_type": name}

            # Add detail from message if available
            if sample_exception and hasattr(sample_exception, "message"):
                value["detail"] = sample_exception.message
            else:
                # Either creation failed or no message attribute
                if error:
                    print(f"Warning: Failed to create example for {name}: {error}")

                # Use class name as fallback
                value["detail"] = f"{readable_name} occurred"

            # Create the example
            example = Example(
                summary=readable_name, description=description, value=value
            )

            examples.append(example)

        return examples

    # Public methods for specific status codes

    @staticmethod
    def create_bad_request_examples(*exception_classes: Type[Any]) -> List[Example]:
        """Generate examples for 400 Bad Request exceptions."""
        return ExampleGenerator._create_examples(exception_classes, 400)

    @staticmethod
    def create_unauthorized_examples(*exception_classes: Type[Any]) -> List[Example]:
        """Generate examples for 401 Unauthorized exceptions."""
        return ExampleGenerator._create_examples(exception_classes, 401)

    @staticmethod
    def create_forbidden_examples(*exception_classes: Type[Any]) -> List[Example]:
        """Generate examples for 403 Forbidden exceptions."""
        return ExampleGenerator._create_examples(exception_classes, 403)

    @staticmethod
    def create_not_found_examples(*exception_classes: Type[Any]) -> List[Example]:
        """Generate examples for 404 Not Found exceptions."""
        return ExampleGenerator._create_examples(exception_classes, 404)

    @staticmethod
    def create_conflict_examples(*exception_classes: Type[Any]) -> List[Example]:
        """Generate examples for 409 Conflict exceptions."""
        return ExampleGenerator._create_examples(exception_classes, 409)

    @staticmethod
    def create_server_error_examples(*exception_classes: Type[Any]) -> List[Example]:
        """Generate examples for 500 Server Error exceptions."""
        return ExampleGenerator._create_examples(exception_classes, 500)

    @staticmethod
    def create_examples_from_exceptions(
        *exception_classes: Type[Any],
    ) -> Dict[int, List[Example]]:
        """Automatically categorize exceptions by status code and generate examples."""
        result = {}

        for exception_class in exception_classes:
            status_code = ExampleGenerator._detect_status_code(exception_class)

            if status_code not in result:
                result[status_code] = []

            result[status_code].extend(
                ExampleGenerator._create_examples([exception_class], status_code)
            )

        return result

    @staticmethod
    def create_examples_for_route(
        exception_mapping: Dict[int, List[Type[Any]]],
    ) -> Dict[int, List[Example]]:
        """Generate examples for a route with predefined status codes and exceptions."""
        result = {}

        for status_code, exceptions in exception_mapping.items():
            result[status_code] = ExampleGenerator._create_examples(
                exceptions, status_code
            )

        return result


COMMON_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: ResponseSpec(
        description="Provided tokens are not valid",
        data_container=ErrorResponse[
            TokenValidationError | TokenExpiredException | TokenRevokedException
        ],
        examples=ExampleGenerator.create_unauthorized_examples(
            TokenValidationError,
            TokenExpiredException,
            TokenRevokedException,
        ),
    ),
    status.HTTP_403_FORBIDDEN: ResponseSpec(
        description="User not allowed to perform operation. User must have required permissions or have valid tokens",
        data_container=ErrorResponse[AccessRejectedException | AccessDeniedException],
        examples=ExampleGenerator.create_forbidden_examples(
            AccessRejectedException, AccessDeniedException
        ),
    ),
}

COMMON_ROLE_RESPONSES = {
    status.HTTP_404_NOT_FOUND: ResponseSpec(
        description="Provided role does not found",
        data_container=ErrorResponse[
            RoleDoesNotExistException | PermissionDoesNotExistException
        ],
        examples=ExampleGenerator.create_not_found_examples(
            RoleDoesNotExistException, PermissionDoesNotExistException
        ),
    ),
}

COMMON_USER_RESPONSES = {
    status.HTTP_404_NOT_FOUND: ResponseSpec(
        description="Provided user does not found",
        data_container=ErrorResponse[
            UserDoesNotExistException | UserIsDeletedException
        ],
        examples=ExampleGenerator.create_not_found_examples(
            UserDoesNotExistException, UserIsDeletedException
        ),
    ),
}

SERVER_ERROR_RESPONSES = {
    status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseSpec(
        description="Internal server error",
        data_container=ErrorResponse[
            AppException
            | ApplicationException
            | InfrastructureException
            | DatabaseException
        ],
        examples=ExampleGenerator.create_server_error_examples(
            AppException,
            ApplicationException,
            InfrastructureException,
            DatabaseException,
        ),
    )
}
