from typing import Annotated, List

from litestar import Controller, Request, Response, route, HttpMethod, status_codes
from litestar.openapi.datastructures import ResponseSpec
from litestar.openapi.spec import Example
from litestar.di import Provide
from litestar.params import Body, Parameter
from dishka import AsyncContainer

from src.application.base.mediator.command import BaseCommandMediator
from src.application.base.mediator.query import BaseQueryMediator
from src.application.cqrs.permission.commands import (
    CreatePermissionCommand,
    DeletePermissionCommand,
)
from src.application.cqrs.permission.queries import GetAllPermissionsQuery
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
from src.application.cqrs.role.queries import GetAllRolesQuery
from src.application.dependency_injector.di import get_container
from src.application.exceptions import (
    ValidationException,
    RoleAlreadyExistsException,
    RoleInUseException,
    PermissionAlreadyExistsException,
    PermissionInUseException,
)
from src.domain.permission.exceptions import WrongPermissionNameFormatException
from src.domain.role.exceptions.role import WrongRoleNameFormatException
from src.infrastructure.exceptions import (
    PermissionDoesNotExistException,
    RoleDoesNotExistException,
)
from src.infrastructure.repositories.pagination import Pagination

from src.presentation.api.v1.base_responses import (
    ExampleGenerator,
    COMMON_RESPONSES,
    COMMON_ROLE_RESPONSES,
    SERVER_ERROR_RESPONSES,
)
from src.presentation.api.exception_configuration import ErrorResponse

import litestar.status_codes as status

import src.domain as domain
import src.application.dto as dto
import src.presentation.api.v1.roles.response as rbac_response
import src.presentation.api.v1.roles.request as rbac_request


class RoleController(Controller):
    path = "/roles"
    tags = ["Roles"]
    security = ([{"BearerToken": []}],)
    dependencies = {"di_container": Provide(get_container)}

    @route(
        path="/",
        http_method=[HttpMethod.POST],
        summary="Create a new role in the system with existing or new permissions",
        description="Create a new role in the system and assign permissions to it. "
        "User must have 'role:create' permission to create a new role. "
        "Role name must be unique and follow the format 'role_name'. Length must be between 2 and 30 characters. "
        "Role security level must be provided. "
        "Role description is optional. "
        "Permissions must be provided as a list of strings. "
        "Permissions must exists in the system. "
        "Permissions must be lowercase alphanumeric with underscores. "
        "Permissions start-length must be between 2 and 15 characters and end between 3 and 30 characters. "
        "Permissions must follow the format 'resource:action[0-9]'.",
        responses={
            status.HTTP_201_CREATED: ResponseSpec(
                description="Role successfully created",
                data_container=rbac_response.CreatedRoleResponseSchema,
            ),
            status.HTTP_400_BAD_REQUEST: ResponseSpec(
                description="Wrong format of provided role name",
                data_container=ErrorResponse[
                    ValidationException | WrongRoleNameFormatException
                ],
                examples=ExampleGenerator.create_bad_request_examples(
                    ValidationException, WrongRoleNameFormatException
                ),
            ),
            status.HTTP_404_NOT_FOUND: ResponseSpec(
                description="Provided permission does not found",
                data_container=ErrorResponse[PermissionDoesNotExistException],
                examples=ExampleGenerator.create_not_found_examples(
                    PermissionDoesNotExistException
                ),
            ),
            status.HTTP_409_CONFLICT: ResponseSpec(
                description="Role with provided name already exists",
                data_container=ErrorResponse[RoleAlreadyExistsException],
                examples=ExampleGenerator.create_conflict_examples(
                    RoleAlreadyExistsException
                ),
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def create_role(
        self,
        di_container: AsyncContainer,
        request: Request,
        data: rbac_request.RoleCreateRequestSchema = Body(),
    ) -> rbac_response.CreatedRoleResponseSchema:

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

            return rbac_response.CreatedRoleResponseSchema.from_entity(role)

    @route(
        path="/",
        http_method=[HttpMethod.GET],
        security=[{}],
        summary="Get all roles and their permissions with pagination.",
        description="Get all roles and their permissions with pagination. "
        "Must be protected in API Gateway.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Roles successfully retrieved",
                data_container=rbac_response.GetRolesResponseSchema,
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def get_all_roles(
        self,
        di_container: AsyncContainer,
        offset: Annotated[
            int,
            Parameter(ge=0, description="Set offset", title="Offset", required=False),
        ] = 0,
        limit: Annotated[
            int,
            Parameter(ge=1, le=1000),
            Parameter(description="Set limit", title="Limit", required=False),
        ] = 100,
    ) -> rbac_response.GetRolesResponseSchema:
        async with di_container() as c:
            query_handler = await c.get(BaseQueryMediator)
            query = GetAllRolesQuery(pagination=Pagination(offset=offset, limit=limit))

            roles: List[domain.Role] = await query_handler.handle_query(query)

            return rbac_response.GetRolesResponseSchema.from_entity(roles)

    @route(
        path="/{role_name:str}",
        http_method=[HttpMethod.DELETE],
        status_code=status_codes.HTTP_200_OK,
        summary="Delete role from the system",
        description="Delete role from the system. "
        "User must have 'role:delete' permission to delete a role. "
        "Role name must be unique and follow the format 'role_name'. Length must be between 2 and 30 characters. "
        "Role must not be assigned to any of users.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Role successfully deleted",
                data_container=Response,
            ),
            status.HTTP_404_NOT_FOUND: ResponseSpec(
                description="Wrong format of provided role name",
                data_container=ErrorResponse[RoleDoesNotExistException],
                examples=ExampleGenerator.create_not_found_examples(
                    RoleDoesNotExistException
                ),
            ),
            status.HTTP_409_CONFLICT: ResponseSpec(
                description="Role with provided name is in use",
                data_container=ErrorResponse[RoleInUseException],
                examples=ExampleGenerator.create_conflict_examples(RoleInUseException),
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
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

    @route(
        path="/{role_name:str}",
        http_method=[HttpMethod.PATCH],
        summary="Partial update of role attributes",
        description="Partial update of role attributes. "
        "User must have 'role:update' permission to update a role. "
        "Only one field can be updated at a time. "
        "Security level can be updated only by system administrators.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Role successfully updated",
                data_container=rbac_response.RoleUpdatedResponseSchema,
            ),
            **COMMON_ROLE_RESPONSES,
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def partial_update_role(
        self,
        di_container: AsyncContainer,
        request: Request,
        role_name: str,
        data: rbac_request.RoleUpdateRequestSchema = Body(),
    ) -> rbac_response.RoleUpdatedResponseSchema:
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
            return rbac_response.RoleUpdatedResponseSchema.from_entity(role)

    @route(
        path="/{role_name:str}/permissions/remove",
        http_method=[HttpMethod.PATCH],
        summary="Remove multiple permissions from a role",
        description="Remove multiple permissions from a role. "
        "User must have 'role:update' permission to update a role.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Role successfully updated",
                data_container=rbac_response.RoleUpdatedResponseSchema,
            ),
            **COMMON_ROLE_RESPONSES,
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def remove_role_permissions(
        self,
        di_container: AsyncContainer,
        request: Request,
        role_name: str,
        data: rbac_request.RemoveRolePermissionsRequestSchema = Body(),
    ) -> rbac_response.RoleUpdatedResponseSchema:
        """Remove multiple permissions from a role"""
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)
            command = RemoveRolePermissionsCommand(
                role_name=role_name,
                new_permissions=data.permissions,
                request=request,
            )

            role, *_ = await command_handler.handle_command(command)
            return rbac_response.RoleUpdatedResponseSchema.from_entity(role)

    @route(
        path="/{role_name:str}/permissions/{permission:str}",
        http_method=[HttpMethod.DELETE],
        status_code=status_codes.HTTP_200_OK,
        summary="Remove a specific permission from a role",
        description="Remove a specific permission from a role. "
        "User must have 'role:update' permission to update a role.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Role successfully updated",
                data_container=rbac_response.RoleUpdatedResponseSchema,
            ),
            **COMMON_ROLE_RESPONSES,
            **COMMON_RESPONSES,
        },
    )
    async def remove_role_permission(
        self,
        di_container: AsyncContainer,
        request: Request,
        role_name: str,
        permission: str,
    ) -> rbac_response.RoleUpdatedResponseSchema:
        """Remove a specific permission from a role"""
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)
            command = RemoveRolePermissionsCommand(
                role_name=role_name,
                new_permissions=[permission],
                request=request,
            )

            role, *_ = await command_handler.handle_command(command)

            return rbac_response.RoleUpdatedResponseSchema.from_entity(role)


class PermissionController(Controller):
    path = "/permissions"
    tags = ["Permissions"]
    security = ([{"BearerToken": []}],)
    dependencies = {"di_container": Provide(get_container)}

    @route(
        path="/",
        http_method=[HttpMethod.GET],
        summary="Get all permissions",
        security=[{}],
        description="Get all permissions. " "Must be protected in API Gateway.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Permissions successfully retrieved",
                data_container=rbac_response.GetPermissionsResponseSchema,
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def get_permissions(
        self,
        di_container: AsyncContainer,
        offset: Annotated[
            int,
            Parameter(ge=0, description="Set offset", title="Offset", required=False),
        ] = 0,
        limit: Annotated[
            int,
            Parameter(ge=1, le=1000),
            Parameter(description="Set limit", title="Limit", required=False),
        ] = 100,
    ) -> rbac_response.GetPermissionsResponseSchema:
        async with di_container() as c:
            query_handler = await c.get(BaseQueryMediator)
            query = GetAllPermissionsQuery(
                pagination=Pagination(offset=offset, limit=limit)
            )

            permissions: List[domain.Permission] = await query_handler.handle_query(
                query
            )

            return rbac_response.GetPermissionsResponseSchema.from_entity(permissions)

    @route(
        path="/",
        http_method=[HttpMethod.POST],
        summary="Create a new permission",
        description="Create a new permission. "
        "User must have 'permission:create' permission to create a permission. "
        "Permissions must be lowercase alphanumeric with underscores. "
        "Permissions start-length must be between 2 and 15 characters and end between 3 and 30 characters. "
        "Permissions must follow the format 'resource:action[0-9]'.",
        responses={
            status.HTTP_201_CREATED: ResponseSpec(
                description="Permission successfully created",
                data_container=rbac_response.CreatedPermissionResponseSchema,
            ),
            status.HTTP_400_BAD_REQUEST: ResponseSpec(
                description="Wrong format of provided permission name",
                data_container=ErrorResponse[
                    ValidationException | WrongPermissionNameFormatException
                ],
                examples=ExampleGenerator.create_bad_request_examples(
                    ValidationException, WrongPermissionNameFormatException
                ),
            ),
            status.HTTP_409_CONFLICT: ResponseSpec(
                description="Permission with given name already exists",
                data_container=ErrorResponse[PermissionAlreadyExistsException],
                examples=ExampleGenerator.create_conflict_examples(
                    PermissionAlreadyExistsException
                ),
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def create_permission(
        self,
        di_container: AsyncContainer,
        request: Request,
        data: rbac_request.PermissionCreateRequestSchema = Body(
            description="Permission to create", title="Permission"
        ),
    ) -> rbac_response.CreatedPermissionResponseSchema:

        async with di_container() as c:

            command_handler = await c.get(BaseCommandMediator)
            command = CreatePermissionCommand(name=data.name, request=request)
            created_permission, *_ = await command_handler.handle_command(command)

            return rbac_response.CreatedPermissionResponseSchema.from_entity(
                created_permission
            )

    @route(
        path="/{permission_name:str}",
        http_method=[HttpMethod.DELETE],
        status_code=status_codes.HTTP_200_OK,
        summary="Delete a specific permission",
        description="Delete a specific permission. "
        "User must have 'permission:delete' permission to delete a permission.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Permission successfully deleted",
                data_container=Response,
                examples=[
                    Example(
                        value={"message": "Permission successfully deleted"},
                        summary="Permission deleted",
                    )
                ],
            ),
            status.HTTP_404_NOT_FOUND: ResponseSpec(
                description="Provided permission does not found",
                data_container=ErrorResponse[PermissionDoesNotExistException],
                examples=ExampleGenerator.create_not_found_examples(
                    PermissionDoesNotExistException
                ),
            ),
            status.HTTP_409_CONFLICT: ResponseSpec(
                description="Permission with provided name is in use",
                data_container=ErrorResponse[PermissionInUseException],
                examples=ExampleGenerator.create_conflict_examples(
                    PermissionInUseException
                ),
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def delete_permission(
        self,
        di_container: AsyncContainer,
        request: Request,
        permission_name: str,
    ) -> Response:
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)
            command = DeletePermissionCommand(name=permission_name, request=request)

            await command_handler.handle_command(command)

            response = Response(
                content={"message": "Permission successfully deleted"},
                status_code=status_codes.HTTP_200_OK,
            )

            return response


class UserRoleController(Controller):
    path = "/user_roles"
    tags = ["User Roles"]
    security = ([{"BearerToken": []}],)
    dependencies = {"di_container": Provide(get_container)}

    @route(
        path="/user/{username:str}/role/{role_name:str}",
        http_method=[HttpMethod.POST],
        summary="Assign a role to a user",
        description="Assign a role to a user. "
        "User must have 'role:assign' permission to assign a role to a user.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Role successfully assigned",
                data_container=rbac_response.RoleAssignedResponseSchema,
            ),
            status.HTTP_404_NOT_FOUND: ResponseSpec(
                description="Provided role does not found",
                data_container=ErrorResponse[RoleDoesNotExistException],
                examples=ExampleGenerator.create_not_found_examples(
                    RoleDoesNotExistException
                ),
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def assign_role(
        self,
        di_container: AsyncContainer,
        request: Request,
        username: str,
        role_name: str,
    ) -> rbac_response.RoleAssignedResponseSchema:
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)
            command = AssignRoleCommand(
                assign_to_user=username,
                role_name=role_name,
                request=request,
            )

            user, *_ = await command_handler.handle_command(command)

            return rbac_response.RoleAssignedResponseSchema.from_entity(user)

    @route(
        path="/user/{username:str}/role/{role_name:str}",
        http_method=[HttpMethod.DELETE],
        status_code=status_codes.HTTP_200_OK,
        summary="Remove a role from a user",
        description="Remove a role from a user. "
        "User must have 'role:remove' permission to remove a role from a user.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Role successfully removed",
                data_container=rbac_response.RoleRemovedResponseSchema,
            ),
            status.HTTP_404_NOT_FOUND: ResponseSpec(
                description="Provided role does not found",
                data_container=ErrorResponse[RoleDoesNotExistException],
                examples=ExampleGenerator.create_not_found_examples(
                    RoleDoesNotExistException
                ),
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def remove_role(
        self,
        di_container: AsyncContainer,
        username: str,
        role_name: str,
        request: Request,
    ) -> rbac_response.RoleRemovedResponseSchema:
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)
            command = RemoveRoleCommand(
                remove_from_user=username,
                role_name=role_name,
                request=request,
            )

            user, *_ = await command_handler.handle_command(command)

            return rbac_response.RoleRemovedResponseSchema.from_entity(user)
