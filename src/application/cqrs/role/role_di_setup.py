from dishka import Scope, provide, Provider

from src.application.cqrs.role.commands import CreateRoleCommandHandler
from src.settings.config import Config


class RoleCommandProvider(Provider):

    create_role = provide(CreateRoleCommandHandler, scope=Scope.REQUEST)
