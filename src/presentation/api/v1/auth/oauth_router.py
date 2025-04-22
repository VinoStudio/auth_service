import secrets
import structlog

from typing import AnyStr
from typing import Dict, Optional, Annotated, Any
from dishka import AsyncContainer
from litestar import Controller, get, post, route, Response, Request
from litestar.di import Provide
from litestar.datastructures import Cookie
from litestar.dto import DTOData
from litestar.enums import RequestEncodingType, HttpMethod
from litestar.exceptions import HTTPException
from litestar.params import Body, Parameter
from litestar.response import Redirect, Response
from litestar.status_codes import (
    HTTP_307_TEMPORARY_REDIRECT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)
from litestar.datastructures import State

from src.application.base.mediator.command import BaseCommandMediator
from src.application.base.security import BaseJWTManager
from src.application.cqrs.user.commands import (
    RegisterUserCommand,
    OAuthLoginUserCommand,
    RegisterOAuthUserCommand,
    AddOAuthAccountToCurrentUserCommand,
    AddOAuthAccountRequestCommand,
)
from src.application.dependency_injector.di import get_container
from src.application.services.security.oauth_manager import OAuthManager

import src.domain as domain
import src.application.dto as dto
from src.infrastructure.repositories import TokenBlackListRepository, TokenType


logger = structlog.getLogger(__name__)


class OAuthController(Controller):
    path = "/oauth"
    tags = ["OAuth"]
    dependencies = {"di_container": Provide(get_container)}

    @route(path="/login/{provider:str}", http_method=[HttpMethod.GET])
    async def oauth_login(
        self, di_container: AsyncContainer, provider: str
    ) -> Redirect:
        """
        Redirect user to OAuth provider login page
        """
        try:
            async with di_container() as c:
                oauth_manager = await c.get(OAuthManager)
                # Generate random state for CSRF protection
                state = secrets.token_urlsafe(32)

                # Get OAuth login URL
                login_url = oauth_manager.get_oauth_url(provider, state)

                # Create redirect response
                response = Redirect(
                    path=login_url,
                    status_code=HTTP_307_TEMPORARY_REDIRECT,
                )

                return response

        except ValueError as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))

    @route(path="/connect/{provider:str}", http_method=[HttpMethod.GET])
    async def oauth_connect(
        self,
        di_container: AsyncContainer,
        provider: str,
        request: Request,
    ) -> Redirect:
        """
        Redirect user to OAuth provider login page
        """
        try:
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
                    status_code=HTTP_307_TEMPORARY_REDIRECT,
                )

                return response

        except ValueError as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))

    @route(
        path="/connect-callback/{provider:str}",
        http_method=[HttpMethod.GET],
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

    @route(path="/callback/{provider:str}", http_method=[HttpMethod.GET])
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

            oauth_data = await oauth_manager.handle_oauth_callback(
                provider_name=provider, code=code, state=state
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

    @route(path="/providers", http_method=[HttpMethod.GET])
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
