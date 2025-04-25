from dataclasses import dataclass
from functools import partial
from typing import TypeVar, Generic, Callable, Optional

import structlog
from litestar import MediaType, Request, Response
from litestar.status_codes import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_410_GONE,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)
from litestar.exceptions import ValidationException as LitestarValidationException

from src.application.base.exception import (
    ApplicationException,
    ResourceNotFoundException,
    ResourceExistsException,
)
from src.application.exceptions import (
    RBACException,
    UnauthorizedRBACOperationException,
)
from src.domain.base.exceptions.application import AppException
from src.domain.base.exceptions.domain import DomainException, ValidationException
from src.infrastructure.base.exception import InfrastructureException
from src.infrastructure.exceptions import (
    DatabaseException,
    RepositoryException,
    UserIsDeletedException,
)
from src.application.exceptions import (
    AuthorizationException,
    AuthenticationException,
)

logger = structlog.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ErrorData(Generic[T]):
    status_code: int
    error_type: str
    detail: str
    data: Optional[T] = None


@dataclass
class ErrorResponse(Generic[T]):
    error: ErrorData[T]


def create_exception_handler(status_code: int) -> Callable:
    """Create an exception handler for a specific status code."""
    return partial(handle_exception, status_code=status_code)


def handle_exception(
    request: Request, exc: Exception, status_code: int = HTTP_500_INTERNAL_SERVER_ERROR
) -> Response:
    """Common exception handling logic."""
    # Log the exception

    exc_name = exc.__class__.__name__
    logger.error(
        f"Exception occurred: {exc_name}",
        path=request.url.path,
        method=request.method,
    )

    # Create error response
    if isinstance(exc, LitestarValidationException):
        validation_errors = getattr(exc, "extra", None)

        error_data = ErrorData(
            status_code=HTTP_400_BAD_REQUEST,
            error_type=exc.__class__.__name__,
            detail=validation_errors[0].get("message") if validation_errors else None,
            data=str(exc),
        )
    else:
        error_data = ErrorData(
            status_code=status_code,
            error_type=exc_name,
            detail=getattr(exc, "message", str(exc)),
        )

    # Return formatted response
    return Response(
        content={"error": error_data.__dict__},
        status_code=status_code,
        media_type=MediaType.JSON,
    )


def handle_unknown_exception(request: Request, exc: Exception) -> Response:
    """Handler for unexpected exceptions."""
    # Log with higher severity
    logger.critical(
        f"Unhandled exception: {exc.__class__.__name__}",
        path=request.url.path,
        method=request.method,
    )

    error_data = ErrorData(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="UnhandledException",
        detail="An unexpected error occurred",
    )

    return Response(
        content={"error": error_data.__dict__},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        media_type=MediaType.JSON,
    )


def setup_exception_handlers():
    """Configure exception handlers with their respective status codes."""
    handlers = {
        # Map exception types to handlers with appropriate status codes
        AppException: create_exception_handler(HTTP_500_INTERNAL_SERVER_ERROR),
        ApplicationException: create_exception_handler(HTTP_500_INTERNAL_SERVER_ERROR),
        DomainException: create_exception_handler(HTTP_400_BAD_REQUEST),
        InfrastructureException: create_exception_handler(
            HTTP_500_INTERNAL_SERVER_ERROR
        ),
        DatabaseException: create_exception_handler(HTTP_500_INTERNAL_SERVER_ERROR),
        ValidationException: create_exception_handler(HTTP_400_BAD_REQUEST),
        RepositoryException: create_exception_handler(HTTP_404_NOT_FOUND),
        ResourceNotFoundException: create_exception_handler(HTTP_404_NOT_FOUND),
        ResourceExistsException: create_exception_handler(HTTP_409_CONFLICT),
        UserIsDeletedException: create_exception_handler(HTTP_409_CONFLICT),
        AuthenticationException: create_exception_handler(HTTP_401_UNAUTHORIZED),
        AuthorizationException: create_exception_handler(HTTP_403_FORBIDDEN),
        RBACException: create_exception_handler(HTTP_403_FORBIDDEN),
        UnauthorizedRBACOperationException: create_exception_handler(
            HTTP_403_FORBIDDEN
        ),
        LitestarValidationException: create_exception_handler(HTTP_400_BAD_REQUEST),
        # Fallback handler for unexpected exceptions
        Exception: handle_unknown_exception,
    }
    return handlers
