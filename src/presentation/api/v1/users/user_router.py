from typing import List, Annotated
from dishka import AsyncContainer

from litestar import Controller, Request, route, HttpMethod
from litestar.di import Provide
from litestar.params import Body, Parameter
from litestar.openapi.datastructures import ResponseSpec
import litestar.status_codes as status


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
    GetCurrentUserConnectedAccounts,
)

from src.infrastructure.repositories.pagination import Pagination
from src.application.dependency_injector.di import get_container

import src.domain as domain
import src.presentation.api.v1.users.response as user_response

from src.presentation.api.v1.base_responses import (
    COMMON_RESPONSES,
    COMMON_USER_RESPONSES,
    SERVER_ERROR_RESPONSES,
)


class UserController(Controller):
    tags = ["Users"]
    path = "/users"
    dependencies = {"di_container": Provide(get_container)}

    @route(
        path="/{user_id:str}",
        http_method=[HttpMethod.GET],
        summary="Get user by provided UUID.",
        description="Get user by provided UUID. ",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="User successfully retrieved",
                data_container=user_response.GetUserResponseSchema,
            ),
            **COMMON_USER_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
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
        summary="Get user by provided username.",
        description="Get user by provided username. ",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="User successfully retrieved",
                data_container=user_response.GetUserResponseSchema,
            ),
            **COMMON_USER_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
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
        security=[{"BearerToken": []}],
        summary="Get current user data",
        description="Get current user id, username and roles",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="User successfully retrieved",
                data_container=user_response.GetUserResponseSchema,
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
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
        security=[{"BearerToken": []}],
        summary="Get current user roles",
        description="Get current user roles",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="User roles successfully retrieved",
                data_container=user_response.GetUserRolesResponseSchema,
            ),
            **COMMON_RESPONSES,
        },
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
        security=[{"BearerToken": []}],
        summary="Get current user permissions",
        description="Get current user permissions",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="User permissions successfully retrieved",
                data_container=user_response.GetUserPermissionsResponseSchema,
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
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
        security=[{"BearerToken": []}],
        summary="Get current user session",
        description="Get current user session",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="User session successfully retrieved",
                data_container=user_response.GetUserSessionResponseSchema,
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
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
        security=[{"BearerToken": []}],
        summary="Get current user sessions",
        description="Get current user sessions",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="User sessions successfully retrieved",
                data_container=user_response.GetUserSessionsResponseSchema,
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
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
        path="/me/connected-accounts",
        http_method=[HttpMethod.GET],
        security=[{"BearerToken": []}],
        summary="Get current user OAuth connected accounts",
        description="Get current user connected accounts",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="User connected accounts successfully retrieved",
                data_container=user_response.GetUserConnectedAccountsResponseSchema,
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def get_current_user_connected_accounts(
        self,
        di_container: AsyncContainer,
        request: Request,
    ) -> user_response.GetUserConnectedAccountsResponseSchema:
        async with di_container() as c:
            query_mediator = await c.get(BaseQueryMediator)
            connected_accounts: List[domain.OAuthAccount] = (
                await query_mediator.handle_query(
                    GetCurrentUserConnectedAccounts(request=request)
                )
            )

        return user_response.GetUserConnectedAccountsResponseSchema.from_entity(
            accounts=connected_accounts
        )

    @route(
        path="/{user_id:str}/roles",
        http_method=[HttpMethod.GET],
        summary="Get user roles",
        description="Get user roles",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="User roles successfully retrieved",
                data_container=user_response.GetUserRolesResponseSchema,
            ),
            **SERVER_ERROR_RESPONSES,
        },
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
        summary="Get user permissions",
        description="Get user permissions",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="User permissions successfully retrieved",
                data_container=user_response.GetUserPermissionsResponseSchema,
            ),
            **SERVER_ERROR_RESPONSES,
        },
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
        summary="Get all users",
        description="Get all users",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Users successfully retrieved",
                data_container=user_response.GetUserResponseSchema,
            ),
            **SERVER_ERROR_RESPONSES,
        },
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
