from typing import List, Annotated

from litestar import Controller, Request, Response, route, HttpMethod
from litestar.di import Provide
from litestar.params import Body, Parameter
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST
from dishka import AsyncContainer

from src.application.base.mediator.command import BaseCommandMediator
from src.application.base.mediator.query import BaseQueryMediator
from src.application.cqrs.user.queries import (
    GetUserByUsername,
    GetUsers,
    GetUserRoles,
    GetCurrentUser,
    GetCurrentUserRoles,
    GetCurrentUserPermissions,
    GetCurrentUserSession,
    GetCurrentUserSessions,
    GetUserById,
    GetUserPermissions,
)
from src.application.dependency_injector.di import get_container

import src.domain as domain
import src.application.dto as dto
import src.presentation.api.v1.users.response as user_response
import src.presentation.api.v1.users.request as user_request
from src.infrastructure.repositories.pagination import Pagination


class UserController(Controller):
    tags = ["Users"]
    path = "/users"
    dependencies = {"di_container": Provide(get_container)}

    @route(
        path="/{user_id:str}",
        http_method=[HttpMethod.GET],
        description="Get user by ID",
    )
    async def get_user_by_id(
        self,
        user_id: Annotated[
            str, Parameter(description="Get user by UUID", title="User ID")
        ],
        di_container: AsyncContainer,
    ) -> user_response.GetUserResponseSchema:

        async with di_container() as c:
            query_mediator = await c.get(BaseQueryMediator)
            user = await query_mediator.handle_query(GetUserById(user_id=user_id))

            return user_response.GetUserResponseSchema.from_entity(user)

    @route(
        path="/username/{username:str}",
        http_method=[HttpMethod.GET],
        description="Get user by username",
    )
    async def get_user_by_username(
        self,
        username: str,
        di_container: AsyncContainer,
    ) -> user_response.GetUserResponseSchema:

        async with di_container() as c:
            query_mediator = await c.get(BaseQueryMediator)
            user = await query_mediator.handle_query(
                GetUserByUsername(username=username)
            )

            return user_response.GetUserResponseSchema.from_entity(user)

    @route(
        path="/me",
        http_method=[HttpMethod.GET],
    )
    async def get_current_user(
        self, di_container: AsyncContainer, request: Request
    ) -> user_response.GetUserResponseSchema:
        async with di_container() as c:
            query_mediator = await c.get(BaseQueryMediator)
            user = await query_mediator.handle_query(GetCurrentUser(request=request))

            return user_response.GetUserResponseSchema.from_entity(user)

    @route(
        path="/me/roles",
        http_method=[HttpMethod.GET],
    )
    async def get_current_user_roles(
        self, di_container: AsyncContainer, request: Request
    ) -> user_response.GetUserRolesResponseSchema:
        async with di_container() as c:
            query_mediator = await c.get(BaseQueryMediator)
            roles = await query_mediator.handle_query(
                GetCurrentUserRoles(request=request)
            )

            return user_response.GetUserRolesResponseSchema(roles=roles)

    @route(
        path="/me/permissions",
        http_method=[HttpMethod.GET],
    )
    async def get_current_user_permissions(
        self, di_container: AsyncContainer, request: Request
    ) -> user_response.GetUserPermissionsResponseSchema:
        async with di_container() as c:
            query_mediator = await c.get(BaseQueryMediator)
            permissions = await query_mediator.handle_query(
                GetCurrentUserPermissions(request=request)
            )

        return user_response.GetUserPermissionsResponseSchema(permissions=permissions)

    @route(
        path="/me/session",
        http_method=[HttpMethod.GET],
    )
    async def get_current_user_session(
        self,
        di_container: AsyncContainer,
        request: Request,
    ) -> user_response.GetUserSessionResponseSchema:
        async with di_container() as c:
            query_mediator = await c.get(BaseQueryMediator)
            session = await query_mediator.handle_query(
                GetCurrentUserSession(request=request)
            )

        return user_response.GetUserSessionResponseSchema.from_entity(session=session)

    @route(
        path="/me/sessions",
        http_method=[HttpMethod.GET],
    )
    async def get_current_user_sessions(
        self,
        di_container: AsyncContainer,
        request: Request,
    ) -> user_response.GetUserSessionsResponseSchema:
        async with di_container() as c:
            query_mediator = await c.get(BaseQueryMediator)
            sessions = await query_mediator.handle_query(
                GetCurrentUserSessions(request=request)
            )

        return user_response.GetUserSessionsResponseSchema.from_entity(
            sessions=sessions
        )

    @route(
        path="/{user_id:str}/roles",
        http_method=[HttpMethod.GET],
        description="Get user roles",
    )
    async def get_user_roles(
        self,
        user_id: str,
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
    ) -> user_response.GetUserRolesResponseSchema:

        async with di_container() as c:
            query_mediator = await c.get(BaseQueryMediator)
            roles = await query_mediator.handle_query(
                GetUserRoles(
                    user_id=user_id,
                    pagination=Pagination(offset=offset, limit=limit),
                )
            )

            return user_response.GetUserRolesResponseSchema(roles=roles)

    @route(
        path="/{user_id:str}/permissions",
        http_method=[HttpMethod.GET],
        description="Get user permissions",
    )
    async def get_user_permissions(
        self,
        user_id: str,
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
    ) -> user_response.GetUserPermissionsResponseSchema:

        async with di_container() as c:
            query_mediator = await c.get(BaseQueryMediator)
            permissions = await query_mediator.handle_query(
                GetUserPermissions(
                    user_id=user_id,
                    pagination=Pagination(offset=offset, limit=limit),
                )
            )

            return user_response.GetUserPermissionsResponseSchema(
                permissions=permissions
            )

    @route(
        path="/",
        http_method=[HttpMethod.GET],
        description="Get all users",
    )
    async def get_all_users(
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
    ) -> List[user_response.GetUserResponseSchema]:

        async with di_container() as c:
            query_mediator = await c.get(BaseQueryMediator)
            users = await query_mediator.handle_query(
                GetUsers(pagination=Pagination(offset=offset, limit=limit))
            )

            return [
                user_response.GetUserResponseSchema.from_entity(user) for user in users
            ]
