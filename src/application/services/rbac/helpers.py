from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from src.application.exceptions import AccessDeniedException

P = ParamSpec("P")
R = TypeVar("R")


def require_permission(
    permission_name: str,
) -> Callable[
    [Callable[..., Coroutine[Any, Any, R]]], Callable[..., Coroutine[Any, Any, R]]
]:
    """Decorator to check if user has required permission"""

    def decorator(
        func: Callable[..., Coroutine[Any, Any, R]],
    ) -> Callable[..., Coroutine[Any, Any, R]]:
        @wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> R:
            # Get user from a consistent position or parameter name
            request_from = kwargs.get("request_from")

            if not request_from:
                raise ValueError("Authorization requires request_from parameter")

            if not self._has_permission(request_from, permission_name):
                raise AccessDeniedException(
                    f"You don't have permission to {permission_name}"
                )

            return await func(self, *args, **kwargs)

        return wrapper

    return decorator
