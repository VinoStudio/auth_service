import secrets
import structlog

from typing import Dict, Any
from dishka import AsyncContainer
from litestar import Controller, route, Response, Request
from litestar.di import Provide

from litestar.enums import HttpMethod
from litestar.params import Body
from litestar.response import Redirect, Response
from litestar.openapi.spec import Example
from litestar.openapi.datastructures import ResponseSpec

import litestar.status_codes as status

from src.application.base.mediator.command import BaseCommandMediator
from src.application.cqrs.user.commands import (
    OAuthLoginUserCommand,
    RegisterOAuthUserCommand,
    AddOAuthAccountToCurrentUserCommand,
    AddOAuthAccountRequestCommand,
    DeactivateUsersOAuthAccountCommand,
)
from src.application.dependency_injector.di import get_container
from src.application.exceptions import (
    OAuthAccountDoesNotExistException,
    OAuthAccountAlreadyDeactivatedException,
    OAuthConnectionTokenExpiredException,
    EmailAlreadyExistsException,
)
from src.application.exceptions.oauth import OAuthAccountAlreadyAssociatedException
from src.application.services.security.oauth_manager import OAuthManager

import src.application.dto as dto
from src.presentation.api.exception_configuration import ErrorResponse
from src.presentation.api.v1.auth.request.user import DisconnectProvider
from src.presentation.api.v1.base_responses import (
    COMMON_RESPONSES,
    ExampleGenerator,
    SERVER_ERROR_RESPONSES,
)

logger = structlog.getLogger(__name__)


class OAuthController(Controller):
    path = "/oauth"
    tags = ["OAuth"]
    dependencies = {"di_container": Provide(get_container)}

    @route(
        path="/login/{provider:str}",
        http_method=[HttpMethod.GET],
        summary="OAuth login",
        description="Redirect user to OAuth provider login page. "
        "OAuth provider name must be provided in query the path.",
        responses={
            status.HTTP_307_TEMPORARY_REDIRECT: ResponseSpec(
                description="Redirect to OAuth provider login page",
                data_container=Response,
                examples=[
                    Example(
                        value={"message": "Redirect to OAuth provider login page"},
                        summary="Redirect",
                    )
                ],
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def oauth_login(
        self, di_container: AsyncContainer, provider: str
    ) -> Redirect:
        """
        Redirect user to OAuth provider login page
        """
        async with di_container() as c:
            oauth_manager = await c.get(OAuthManager)
            # Generate random state for CSRF protection
            state = secrets.token_urlsafe(32)

            # Get OAuth login URL
            login_url = oauth_manager.get_oauth_url(provider, state)

            # Create redirect response
            response = Redirect(
                path=login_url,
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            )

            return response

    @route(
        path="/connect/{provider:str}",
        http_method=[HttpMethod.GET],
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        security=[{"BearerToken": []}],
        summary="OAuth connect third-party provider",
        description="Redirect user to OAuth provider login page. "
        "OAuth provider name must be provided in query the path. "
        "User can add unlimited third-party providers, "
        "as long as combination of provider name and provider's user id is unique.",
        responses={
            status.HTTP_307_TEMPORARY_REDIRECT: ResponseSpec(
                description="Redirect to OAuth provider login page",
                data_container=Response,
                examples=[
                    Example(
                        value={"message": "Redirect to OAuth provider login page"},
                        summary="Redirect",
                    )
                ],
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def oauth_connect(
        self,
        di_container: AsyncContainer,
        provider: str,
        request: Request,
    ) -> Redirect:
        """
        Redirect user to OAuth provider login page
        """
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)

            command = AddOAuthAccountRequestCommand(
                provider=provider,
                request=request,
            )

            login_url, *_ = await command_handler.handle_command(command)

            # Create redirect response
            response = Redirect(
                path=login_url,
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            )

            return response

    @route(
        path="/connect-callback/{provider:str}",
        http_method=[HttpMethod.GET],
        summary="OAuth connect third-party provider callback",
        description="Handle's OAuth callback. "
        "It will create a new third-party account association with current user. "
        "If account already exists, but has been deactivated, it will be reactivated. "
        "If account exists and active, raises error.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Successfully connected to provider",
                data_container=Response,
                examples=[
                    Example(
                        value={"message": "Successfully connected to provider"},
                        summary="Connected",
                    )
                ],
            ),
            status.HTTP_404_NOT_FOUND: ResponseSpec(
                description="Connection token expired",
                data_container=ErrorResponse[OAuthConnectionTokenExpiredException],
                examples=ExampleGenerator.create_not_found_examples(
                    OAuthConnectionTokenExpiredException
                ),
            ),
            status.HTTP_409_CONFLICT: ResponseSpec(
                description="Account is already connected to user",
                data_container=ErrorResponse[OAuthAccountAlreadyAssociatedException],
                examples=ExampleGenerator.create_conflict_examples(
                    OAuthAccountAlreadyAssociatedException
                ),
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def oauth_connect_callback(
        self,
        di_container: AsyncContainer,
        provider: str,
        request: Request,
    ) -> Response:
        """
        Handle OAuth callback and create user session and register user if it needs to
        """
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)
            response = Response(content="")

            code = request.query_params.get("code")
            state = request.query_params.get("state")

            command = AddOAuthAccountToCurrentUserCommand(
                provider=provider, code=code, state=state
            )

            await command_handler.handle_command(command)

            response.content = {
                "message": f"Successfully connected to provider {provider}"
            }

            return response

    @route(
        path="/callback/{provider:str}",
        http_method=[HttpMethod.GET],
        summary="OAuth authentication callback",
        description="Handle's OAuth callback. "
        "If user doesn't exist, it will be created as normal auth flow user. "
        "If user exists, it will pass registration to session creation and token pair generation.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Successfully authenticated",
                data_container=Response,
                examples=[
                    Example(
                        value={"access_token": "access_token"},
                        summary="Authenticated",
                    )
                ],
            ),
            status.HTTP_409_CONFLICT: ResponseSpec(
                description="Email already exists in system",
                data_container=ErrorResponse[EmailAlreadyExistsException],
                examples=ExampleGenerator.create_conflict_examples(
                    EmailAlreadyExistsException
                ),
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def oauth_callback(
        self,
        di_container: AsyncContainer,
        request: Request,
        provider: str,
    ) -> Response:
        """
        Handle OAuth callback and create user session and register user if it needs to
        """
        async with di_container() as c:
            oauth_manager = await c.get(OAuthManager)
            command_handler = await c.get(BaseCommandMediator)
            response = Response(content="")

            code = request.query_params.get("code")
            state = request.query_params.get("state")

            oauth_data: dto.OauthUserCredentials | dto.OAuthUserIdentity = (
                await oauth_manager.handle_oauth_callback(
                    provider_name=provider, code=code, state=state
                )
            )

            user_id = None
            jwt_data = None

            # Handle registration if needed
            if isinstance(oauth_data, dto.OauthUserCredentials):
                register_command = RegisterOAuthUserCommand(
                    oauth_info=oauth_data,
                )
                user, *_ = await command_handler.handle_command(register_command)
                user_id = user.id.to_raw()
                jwt_data = user.jwt_data

            else:
                # User already exists, use the identity info
                user_id = oauth_data.user_id
                jwt_data = oauth_data.jwt_data

            # Login the user
            login_command = OAuthLoginUserCommand(
                user_id=user_id,
                jwt_data=jwt_data,
                request=request,
                response=response,
            )

            tokens, *_ = await command_handler.handle_command(login_command)
            response.content = {"access_token": tokens.access_token}
            return response

    @route(
        path="/providers",
        http_method=[HttpMethod.GET],
        summary="Get list of supported OAuth providers",
        description="Get list of supported OAuth providers",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="List of supported OAuth providers",
                data_container=Response,
                examples=[
                    Example(
                        value={
                            "providers": {
                                "google": {
                                    "name": "google",
                                    "login_url": "/oauth/login/google",
                                }
                            }
                        },
                        summary="Provider's list",
                    )
                ],
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def get_providers(
        self,
        di_container: AsyncContainer,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get list of supported OAuth providers
        """

        async with di_container() as c:
            oauth_manager = await c.get(OAuthManager)
            providers = {}
            for provider_name in oauth_manager.oauth_provider_factory.providers:
                providers[provider_name] = {
                    "name": provider_name,
                    "login_url": f"/oauth/login/{provider_name}",
                }

            return {"providers": providers}

    @route(
        path="/disconnect",
        http_method=[HttpMethod.DELETE],
        status_code=status.HTTP_200_OK,
        security=[{"BearerToken": []}],
        summary="Disconnect user from OAuth provider",
        description="Disconnect user from OAuth provider with specified provider name and provider's user id. "
        "Provider name and provider's user id must be provided in the request body.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Successfully disconnected from provider",
                data_container=Response,
                examples=[
                    Example(
                        value="{'message': 'Successfully disconnected from provider'}",
                    )
                ],
            ),
            status.HTTP_404_NOT_FOUND: ResponseSpec(
                description="Associated account cannot be found",
                data_container=ErrorResponse[OAuthAccountDoesNotExistException],
                examples=ExampleGenerator.create_not_found_examples(
                    OAuthAccountDoesNotExistException
                ),
            ),
            status.HTTP_409_CONFLICT: ResponseSpec(
                description="Account is already deactivated",
                data_container=ErrorResponse[OAuthAccountAlreadyDeactivatedException],
                examples=ExampleGenerator.create_conflict_examples(
                    OAuthAccountAlreadyDeactivatedException
                ),
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def oauth_disconnect(
        self,
        di_container: AsyncContainer,
        request: Request,
        data: DisconnectProvider = Body(description="OAuth provider data"),
    ) -> Response:
        """
        Disconnect user from OAuth provider
        """
        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)

            command = DeactivateUsersOAuthAccountCommand(
                provider_name=data.provider_name,
                provider_user_id=data.provider_user_id,
                request=request,
            )

            await command_handler.handle_command(command)

            response = Response(
                content={"message": "Successfully disconnected from provider"}
            )

            return response
