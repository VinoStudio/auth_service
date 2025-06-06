from dishka import Provider, Scope, provide

from src.application.cqrs.permission.commands import (
    CreatePermissionCommandHandler,
    DeletePermissionCommandHandler,
)
from src.application.cqrs.permission.queries import (
    GetAllPermissionsHandler,
)


class PermissionCommandProvider(Provider):
    # Command handlers
    create_permission = provide(CreatePermissionCommandHandler, scope=Scope.REQUEST)
    delete_permission = provide(DeletePermissionCommandHandler, scope=Scope.REQUEST)


class PermissionQueryProvider(Provider):
    # Query handlers
    get_permissions = provide(GetAllPermissionsHandler, scope=Scope.REQUEST)
