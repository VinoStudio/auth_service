from functools import wraps
from typing import Callable, TypeVar, Any, ParamSpec, Coroutine
from src.application.services.security.security_user import SecurityUser

Param = ParamSpec("Param")
ReturnType = TypeVar("ReturnType")
Func = Callable[Param, ReturnType]


def authorization_required(
    func: Callable[Param, Coroutine[Any, Any, ReturnType]],
) -> Callable[Param, Coroutine[Any, Any, ReturnType]]:
    """
    Decorator for command handlers that extracts and validates JWT token from request,
    creates a SecurityUser, and makes it available to the handler method.

    This decorator handles the common pattern:
    1. Extract token from Authorization header
    2. Validate the token
    3. Create SecurityUser from token data

    The decorated method can access the security_user through func parameter
    """

    @wraps(func)
    async def wrapper(self, command: Any, *args, **kwargs) -> ReturnType:
        # Extract and validate token
        token = self._jwt_manager.get_access_token_from_request(command.request)
        token_data = await self._jwt_manager.validate_token(token)

        # Create security user
        security_user = SecurityUser.create_from_token_dto(token_data)

        # Call the original method
        return await func(self, command, security_user, *args, **kwargs)

    return wrapper
