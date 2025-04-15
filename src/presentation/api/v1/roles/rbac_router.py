from litestar import Controller, Request, Response, route, HttpMethod, status_codes
from litestar.di import Provide
from litestar.params import Body
from litestar.exceptions import HTTPException
from dishka import AsyncContainer

from src.application.base.mediator.command import BaseCommandMediator
from src.application.cqrs.role.commands import (
    CreateRoleCommand,
    DeleteRoleCommand,
    AssignRoleCommand,
    RemoveRoleCommand,
    UpdateRolePermissionsCommand,
    UpdateRoleDescriptionCommand,
    UpdateRoleSecurityLvlCommand,
    RemoveRolePermissionsCommand,
)
from src.application.dependency_injector.di import get_container

import src.domain as domain
import src.application.dto as dto
import src.presentation.api.v1.roles.response as role_response
import src.presentation.api.v1.roles.request as role_request


class RBACController(Controller):
    path = "/roles"
    tags = ["RBAC"]
    dependencies = {"di_container": Provide(get_container)}

    @route(path="/", http_method=[HttpMethod.POST])
    async def create_role(
        self,
        di_container: AsyncContainer,
        request: Request,
        data: role_request.RoleCreateRequestSchema = Body(),
    ) -> role_response.CreatedRoleResponseSchema:

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

    @route(
        path="/{role_name:str}",
        http_method=[HttpMethod.DELETE],
        status_code=status_codes.HTTP_200_OK,
    )
    async def delete_role(
        self,
        di_container: AsyncContainer,
        role_name: str,
        request: Request,
    ) -> Response:

        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)
            command = DeleteRoleCommand(
                role_name=role_name,
                request=request,
            )

            await command_handler.handle_command(command)

            return Response(
                content={"message": "Role successfully deleted"},
                status_code=status_codes.HTTP_200_OK,
            )

    # @route(path="/{role_name:str}", http_method=[HttpMethod.PUT])
    # async def update_role(
    #     self,
    #     di_container: AsyncContainer,
    #     request: Request,
    #     role_name: str,
    #     data: RoleUpdateRequestSchema = Body(),
    # ) -> role_response.RoleUpdatedResponseSchema:
    #     """Complete replacement of a role (requires all fields)"""
    #     async with di_container() as c:
    #         command_handler = await c.get(BaseCommandMediator)
    #         command = UpdateRoleCommand(
    #             role_name=role_name,
    #             description=data.description,
    #             security_level=data.security_level,
    #             permissions=data.permissions,
    #             request=request,
    #         )
    #
    #         role, *_ = await command_handler.handle_command(command)
    #         return role_response.RoleUpdatedResponseSchema.from_entity(role)

    @route(path="/{role_name:str}", http_method=[HttpMethod.PATCH])
    async def partial_update_role(
        self,
        di_container: AsyncContainer,
        request: Request,
        role_name: str,
        data: role_request.RoleUpdateRequestSchema = Body(),
    ) -> role_response.RoleUpdatedResponseSchema:
        """Partial update of role attributes"""
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)

            if data.security_level is not None:
                command = UpdateRoleSecurityLvlCommand(
                    role_name=role_name,
                    new_security_lvl=data.security_level,
                    request=request,
                )
            elif data.description is not None:
                command = UpdateRoleDescriptionCommand(
                    role_name=role_name,
                    new_description=data.description,
                    request=request,
                )
            elif data.permissions is not None:
                command = UpdateRolePermissionsCommand(
                    role_name=role_name,
                    new_permissions=data.permissions,
                    request=request,
                )

            role, *_ = await command_handler.handle_command(command)
            return role_response.RoleUpdatedResponseSchema.from_entity(role)

    @route(path="/{role_name:str}/permissions/remove", http_method=[HttpMethod.PATCH])
    async def remove_role_permissions(
        self,
        di_container: AsyncContainer,
        request: Request,
        role_name: str,
        data: role_request.RemoveRolePermissionsRequestSchema = Body(),
    ) -> role_response.RoleUpdatedResponseSchema:
        """Remove multiple permissions from a role"""
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)
            command = RemoveRolePermissionsCommand(
                role_name=role_name,
                new_permissions=data.permissions,
                request=request,
            )

            role, *_ = await command_handler.handle_command(command)
            return role_response.RoleUpdatedResponseSchema.from_entity(role)

    @route(
        path="/{role_name:str}/permissions/{permission:str}",
        http_method=[HttpMethod.DELETE],
        status_code=status_codes.HTTP_200_OK,
    )
    async def remove_role_permission(
        self,
        di_container: AsyncContainer,
        request: Request,
        role_name: str,
        permission: str,
    ) -> role_response.RoleUpdatedResponseSchema:
        """Remove a specific permission from a role"""
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)
            command = RemoveRolePermissionsCommand(
                role_name=role_name,
                new_permissions=[permission],
                request=request,
            )

            role, *_ = await command_handler.handle_command(command)
            return role_response.RoleUpdatedResponseSchema.from_entity(role)


class UserRoleController(Controller):
    path = "/user_roles"
    tags = ["User Roles"]
    dependencies = {"di_container": Provide(get_container)}

    @route(
        path="/user/{username:str}/role/{role_name:str}", http_method=[HttpMethod.POST]
    )
    async def assign_role(
        self,
        di_container: AsyncContainer,
        request: Request,
        username: str,
        role_name: str,
    ) -> role_response.RoleAssignedResponseSchema:
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)
            command = AssignRoleCommand(
                assign_to_user=username,
                role_name=role_name,
                request=request,
            )

            user, *_ = await command_handler.handle_command(command)

            return role_response.RoleAssignedResponseSchema.from_entity(user)

    @route(
        path="/user/{username:str}/role/{role_name:str}",
        http_method=[HttpMethod.DELETE],
        status_code=status_codes.HTTP_200_OK,
    )
    async def remove_role(
        self,
        di_container: AsyncContainer,
        username: str,
        role_name: str,
        request: Request,
    ) -> role_response.RoleRemovedResponseSchema:
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)
            command = RemoveRoleCommand(
                remove_from_user=username,
                role_name=role_name,
                request=request,
            )

            user, *_ = await command_handler.handle_command(command)

            return role_response.RoleRemovedResponseSchema.from_entity(user)
