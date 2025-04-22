from litestar import Controller, Request, Response, route, HttpMethod
from litestar.di import Provide
from litestar.params import Body
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST
from litestar.openapi.datastructures import ResponseSpec
from dishka import AsyncContainer


from src.application.base.mediator.command import BaseCommandMediator
from src.application.cqrs.user.commands import (
    RegisterUserCommand,
    LoginUserCommand,
    RefreshUserTokensCommand,
    LogoutUserCommand,
    ResetPasswordRequestCommand,
    ResetUserPasswordCommand,
    ChangeEmailRequestCommand,
    ChangeUserEmailCommand,
)
from src.application.dependency_injector.di import get_container

from src.presentation.api.v1.auth.response.user import (
    CreateUserResponseSchema,
)

import src.presentation.api.v1.auth.request.user as user_requests
import litestar.status_codes as status


class AuthController(Controller):
    path = "/auth"
    tags = ["Auth"]
    dependencies = {"di_container": Provide(get_container)}

    @route(
        path="/register",
        http_method=[HttpMethod.POST],
        tags=["public"],
        summary="Register a new user account in the API.",
        description="Creates a new user with the provided credentials and future profile information. "
        "Username and email must be unique. "
        "Password has to be at least 8 characters long and contain at least one number, one lowercase letter and one uppercase letter. "
        "Fullname detail should be provided for user service communication.",
        responses={
            status.HTTP_201_CREATED: ResponseSpec(
                description="User successfully registered",
                data_container=CreateUserResponseSchema,
            ),
        },
    )
    async def register(
        self,
        di_container: AsyncContainer,
        request: Request,
        data: user_requests.UserCreate = Body(),
    ) -> CreateUserResponseSchema:
        """
        Raises:
            400 Bad Request:
                - "Email already in use": Another account exists with this email
                - "Username already taken": Another account exists with this username
                - "Password too weak": Password doesn't meet complexity requirements

            422 Unprocessable Entity:
                - Validation errors for required or malformed fields

        Notes:
            - Triggers a welcome email to the user's email address
            - Password is stored securely using bcrypt hashing
        """

        async with di_container() as c:
            command_handler = await c.get(BaseCommandMediator)
            command = RegisterUserCommand(
                email=data.email,
                password=data.password,
                username=data.username,
                request=request,
                first_name=data.first_name,
                last_name=data.last_name,
                middle_name=data.middle_name,
            )

            user, *_ = await command_handler.handle_command(command)

            return CreateUserResponseSchema.from_entity(user)

    @route(
        path="/login",
        http_method=[HttpMethod.POST],
        tags=["public"],
        security=[{"BearerToken": []}],
    )
    async def login(
        self,
        di_container: AsyncContainer,
        request: Request,
        data: user_requests.UserLogin = Body(
            description="Login with email and get refresh tokens", title="UserLogin"
        ),
    ) -> Response:
        async with di_container() as c:
            response: Response = Response(content=None)
            command_handler = await c.get(BaseCommandMediator)
            command = LoginUserCommand(
                email_or_username=data.email,
                password=data.password,
                request=request,
                response=response,
            )

            tokens, *_ = await command_handler.handle_command(command)

            response.content = {"access_token": tokens.access_token}

            return response

    @route(path="/refresh", http_method=[HttpMethod.POST])
    async def refresh_token(
        self,
        di_container: AsyncContainer,
        request: Request,
    ) -> Response:
        async with di_container() as c:
            response: Response = Response(content=None)
            command_handler = await c.get(BaseCommandMediator)
            command = RefreshUserTokensCommand(
                request=request,
                response=response,
            )

            tokens, *_ = await command_handler.handle_command(command)

            response.content = {"access_token": tokens.access_token}

            return response

    @route(path="/logout", http_method=[HttpMethod.POST])
    async def logout(
        self,
        di_container: AsyncContainer,
        request: Request,
    ) -> Response:
        async with di_container() as c:
            response: Response = Response(content=None)
            command_handler = await c.get(BaseCommandMediator)

            command = LogoutUserCommand(
                request=request,
                response=response,
            )

            await command_handler.handle_command(command)

            response.content = {"message": "Successfully logged out"}

            return response

    @route(path="/password-reset/request", http_method=[HttpMethod.POST])
    async def reset_password(
        self,
        di_container: AsyncContainer,
        data: user_requests.PasswordResetRequest = Body(
            description="Request password reset", title="Password Reset"
        ),
    ) -> Response:
        async with di_container() as c:
            response: Response = Response(content=None)
            command_handler = await c.get(BaseCommandMediator)

            command = ResetPasswordRequestCommand(email=data.email)

            await command_handler.handle_command(command)

            response.content = {"message": "Email of password reset has been sent"}

            return response

    @route(path="/password-reset/confirm", http_method=[HttpMethod.POST])
    async def confirm_password_reset(
        self,
        di_container: AsyncContainer,
        data: user_requests.PasswordReset = Body(
            description="Confirm password reset", title="Password Reset"
        ),
    ) -> Response:
        async with di_container() as c:
            response: Response = Response(content=None)
            command_handler = await c.get(BaseCommandMediator)

            command = ResetUserPasswordCommand(
                token=data.token,
                new_password=data.new_password,
            )

            await command_handler.handle_command(command)

            response.content = {"message": "Password successfully has been reset"}

            return response

    @route(path="/email-change/request", http_method=[HttpMethod.POST])
    async def change_email(
        self,
        di_container: AsyncContainer,
        data: user_requests.EmailChangeRequest = Body(
            description="Request to change user email", title="Change Email"
        ),
    ) -> Response:
        async with di_container() as c:
            response: Response = Response(content=None)
            command_handler = await c.get(BaseCommandMediator)

            command = ChangeEmailRequestCommand(email=data.email)

            await command_handler.handle_command(command)

            response.content = {"message": "Notification of email change has been sent"}

            return response

    @route(path="/email-change/confirm", http_method=[HttpMethod.POST])
    async def confirm_email_change(
        self,
        di_container: AsyncContainer,
        data: user_requests.EmailChange = Body(
            description="Confirm email change", title="Email Change"
        ),
    ) -> Response:
        async with di_container() as c:
            response: Response = Response(content=None)
            command_handler = await c.get(BaseCommandMediator)

            command = ChangeUserEmailCommand(
                token=data.token,
                new_email=data.new_email,
            )

            await command_handler.handle_command(command)

            response.content = {"message": "Email successfully has been changed"}

            return response
