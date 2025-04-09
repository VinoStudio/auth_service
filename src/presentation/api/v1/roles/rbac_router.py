from litestar import Controller, Request, Response, route, HttpMethod
from litestar.di import Provide
from litestar.params import Body
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST
from dishka import AsyncContainer

from src.application.base.mediator.command import BaseCommandMediator
from src.application.cqrs.role.commands.create_role import CreateRoleCommand
from src.application.dependency_injector.di import get_container

import src.domain as domain
import src.application.dto as dto
import src.presentation.api.v1.roles.response as role_response
import src.presentation.api.v1.roles.request as role_request


class RBACController(Controller):
    path = "/role"
    dependencies = {"di_container": Provide(get_container)}

    @route(path="/create", http_method=[HttpMethod.POST], sync_to_thread=False)
    async def register(
        self,
        di_container: AsyncContainer,
        request: Request,
        data: role_request.RoleCreateRequestSchema = Body(),
    ) -> role_response.CreatedRoleResponseSchema:

        try:
            async with di_container() as c:
                command_handler = await c.get(BaseCommandMediator)
                command = CreateRoleCommand(
                    name=data.name,
                    description=data.description,
                    security_level=data.security_level,
                    permissions=data.permissions,
                    request=request,
                )

                role, *_ = await command_handler.handle_command(command)

                return role_response.CreatedRoleResponseSchema.from_entity(role)
        except Exception as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
