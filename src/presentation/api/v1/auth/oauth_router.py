import secrets
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

from src.application.base.mediator.command import BaseCommandMediator
from src.application.cqrs.user.commands import (
    RegisterUserCommand,
    OAuthLoginUserCommand,
)
from src.application.dependency_injector.di import get_container
from src.application.services.security.oauth_manager import OAuthManager

import src.domain as domain
import src.application.dto as dto


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
                login_url = oauth_manager.get_oauth_login_url(provider, state)

                # Create redirect response
                response = Redirect(
                    path=login_url,
                    status_code=HTTP_307_TEMPORARY_REDIRECT,
                )

                return response

        except ValueError as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))

    @route(path="/callback/{provider:str}", http_method=[HttpMethod.GET])
    async def oauth_callback(
        self,
        di_container: AsyncContainer,
        request: Request,
        provider: str,
        code: str = Body(),
    ) -> Response:
        """
        Handle OAuth callback and create user session and register user if it needs to
        """
        try:
            async with di_container() as c:
                oauth_manager = await c.get(OAuthManager)
                command_handler = await c.get(BaseCommandMediator)
                response = Response(content="")

                user: dto.OauthUserCredentials | domain.User = (
                    await oauth_manager.handle_oauth_callback(
                        provider_name=provider,
                        code=code,
                        response=response,
                    )
                )
                if isinstance(user, dto.OauthUserCredentials):
                    register_command = RegisterUserCommand(
                        email=user.email,
                        username=user.username,
                        password=user.password,
                        request=request,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        middle_name=user.middle_name,
                    )

                    user, *_ = await command_handler.handle_command(register_command)

                oauth_login_command = OAuthLoginUserCommand(
                    user_id=user.id.to_raw(),
                    jwt_data=user.jwt_data,
                    request=request,
                    response=response,
                )

                tokens, *_ = await command_handler.handle_command(oauth_login_command)

                response.content = {"access_token": tokens.access_token}

                return response

        except Exception as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"OAuth authentication failed: {str(e)}",
            )

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
