from dishka import Scope, provide, Provider

from src.application.cqrs.role.commands import (
    CreateRoleCommandHandler,
    AssignRoleCommandHandler,
    DeleteRoleCommandHandler,
    RemoveRoleCommandHandler,
    UpdateRoleSecurityLvlCommandHandler,
    UpdateRoleDescriptionCommandHandler,
    UpdateRolePermissionsCommandHandler,
    RemoveRolePermissionsCommandHandler,
)
from src.settings.config import Config


class RoleCommandProvider(Provider):

    create_role = provide(CreateRoleCommandHandler, scope=Scope.REQUEST)

    assign_role = provide(AssignRoleCommandHandler, scope=Scope.REQUEST)

    delete_role = provide(DeleteRoleCommandHandler, scope=Scope.REQUEST)

    remove_role = provide(RemoveRoleCommandHandler, scope=Scope.REQUEST)

    update_role_security_lvl = provide(
        UpdateRoleSecurityLvlCommandHandler, scope=Scope.REQUEST
    )

    update_role_description = provide(
        UpdateRoleDescriptionCommandHandler, scope=Scope.REQUEST
    )

    update_role_permissions = provide(
        UpdateRolePermissionsCommandHandler, scope=Scope.REQUEST
    )

    remove_role_permissions = provide(
        RemoveRolePermissionsCommandHandler, scope=Scope.REQUEST
    )
