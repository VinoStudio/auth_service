from litestar import MediaType, Request, Response
from litestar.status_codes import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_410_GONE,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)

from src.application.base.exception import ApplicationException
from src.application.exceptions import (
    UsernameAlreadyExistsException,
    RBACException,
    UnauthorizedRBACOperationException,
)
from src.domain.base.exceptions.application import AppException
from src.domain.base.exceptions.domain import DomainException, ValidationException
from src.infrastructure.base.exception import InfrastructureException
from src.infrastructure.exceptions import (
    DatabaseException,
    UserDoesNotExistException,
    UserWithUsernameDoesNotExistException,
    UserIdAlreadyExistsErrorException,
    UserIsDeletedException,
)
from src.application.exceptions import (
    AuthorizationException,
    AuthenticationException,
    AccessRejectedException,
)


# Individual exception handlers
def app_exception_handler(request: Request, exc: AppException) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        media_type=MediaType.JSON,
    )


def application_exception_handler(
    request: Request, exc: ApplicationException
) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        media_type=MediaType.JSON,
    )


def domain_exception_handler(request: Request, exc: DomainException) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        media_type=MediaType.JSON,
    )


def infrastructure_exception_handler(
    request: Request, exc: InfrastructureException
) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        media_type=MediaType.JSON,
    )


def database_exception_handler(request: Request, exc: DatabaseException) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        media_type=MediaType.JSON,
    )


def validation_exception_handler(
    request: Request, exc: ValidationException
) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        media_type=MediaType.JSON,
    )


def user_not_exist_handler(
    request: Request, exc: UserDoesNotExistException
) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_404_NOT_FOUND,
        media_type=MediaType.JSON,
    )


def username_not_exist_handler(
    request: Request, exc: UserWithUsernameDoesNotExistException
) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_404_NOT_FOUND,
        media_type=MediaType.JSON,
    )


def username_exists_handler(
    request: Request, exc: UsernameAlreadyExistsException
) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_409_CONFLICT,
        media_type=MediaType.JSON,
    )


def user_id_exists_handler(
    request: Request, exc: UserIdAlreadyExistsErrorException
) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_409_CONFLICT,
        media_type=MediaType.JSON,
    )


def user_deleted_handler(request: Request, exc: UserIsDeletedException) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_410_GONE,
        media_type=MediaType.JSON,
    )


def unauthorized_handler(request: Request, exc: AuthenticationException) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_401_UNAUTHORIZED,
        media_type=MediaType.JSON,
    )


def forbidden_exception_handler(
    request: Request, exc: AuthorizationException
) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_403_FORBIDDEN,
        media_type=MediaType.JSON,
    )


def rbac_exception_handler(request: Request, exc: RBACException) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_409_CONFLICT,
        media_type=MediaType.JSON,
    )


def rbac_unauthorized_handler(
    request: Request, exc: UnauthorizedRBACOperationException
) -> Response:
    return Response(
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
            }
        },
        status_code=HTTP_401_UNAUTHORIZED,
        media_type=MediaType.JSON,
    )


def get_exception_handlers():
    return {
        # Map exception types to handlers
        AppException: app_exception_handler,
        ApplicationException: application_exception_handler,
        DomainException: domain_exception_handler,
        InfrastructureException: infrastructure_exception_handler,
        DatabaseException: database_exception_handler,
        ValidationException: validation_exception_handler,
        UserDoesNotExistException: user_not_exist_handler,
        UserWithUsernameDoesNotExistException: username_not_exist_handler,
        UsernameAlreadyExistsException: username_exists_handler,
        UserIdAlreadyExistsErrorException: user_id_exists_handler,
        UserIsDeletedException: user_deleted_handler,
        AuthenticationException: unauthorized_handler,
        AuthorizationException: forbidden_exception_handler,
        RBACException: rbac_exception_handler,
        UnauthorizedRBACOperationException: rbac_unauthorized_handler,
    }
