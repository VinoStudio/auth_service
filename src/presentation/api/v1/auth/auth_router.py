import litestar.status_codes as status
from dishka import AsyncContainer
from litestar import Controller, HttpMethod, Request, Response, route
from litestar.di import Provide
from litestar.exceptions import ValidationException as LitestarValidationException
from litestar.openapi.datastructures import ResponseSpec
from litestar.openapi.spec import Example
from litestar.params import Body

import src.presentation.api.v1.auth.request.user as user_requests
from src.application.base.mediator.command import BaseCommandMediator
from src.application.cqrs.user.commands import (
    ChangeEmailRequestCommand,
    ChangeUserEmailCommand,
    LoginUserCommand,
    LogoutUserCommand,
    RefreshUserTokensCommand,
    RegisterUserCommand,
    ResetPasswordRequestCommand,
    ResetUserPasswordCommand,
)
from src.application.dependency_injector.di import get_container
from src.application.exceptions import (
    EmailAlreadyExistsException,
    EmailTokenExpiredException,
    PasswordIsInvalidException,
    PasswordTokenExpiredException,
    UsernameAlreadyExistsException,
)
from src.domain.base.exceptions.domain import ValidationException
from src.domain.user.exceptions import (
    PasswordDoesNotMatchException,
    UsernameIsTooLongException,
    UsernameIsTooShortException,
    WrongEmailFormatException,
    WrongPasswordFormatException,
    WrongUsernameFormatException,
)
from src.infrastructure.exceptions import UserDoesNotExistException
from src.presentation.api.exception_configuration import ErrorResponse
from src.presentation.api.v1.auth.response.user import (
    CreateUserResponseSchema,
)
from src.presentation.api.v1.base_responses import (
    COMMON_RESPONSES,
    SERVER_ERROR_RESPONSES,
    ExampleGenerator,
)


class AuthController(Controller):
    path = "/auth"
    tags = ["Authentication"]
    dependencies = {"di_container": Provide(get_container)}

    @route(
        path="/register",
        http_method=[HttpMethod.POST],
        summary="Register a new user account in the API.",
        description="Creates a new user with the provided credentials and future profile information. "
        "Username and email must be unique. "
        "Password has to be at least 8 characters long and contain: "
        "at least one number, one lowercase letter and one uppercase letter. "
        "Fullname detail should be provided for user service communication.",
        responses={
            status.HTTP_201_CREATED: ResponseSpec(
                description="User successfully registered",
                data_container=CreateUserResponseSchema,
            ),
            status.HTTP_409_CONFLICT: ResponseSpec(
                description="Email or username already in use",
                data_container=ErrorResponse[
                    EmailAlreadyExistsException | UsernameAlreadyExistsException
                ],
                examples=ExampleGenerator.create_conflict_examples(
                    EmailAlreadyExistsException, UsernameAlreadyExistsException
                ),
            ),
            status.HTTP_400_BAD_REQUEST: ResponseSpec(
                description="Bad request. Wrong format of fulfillment data",
                data_container=ErrorResponse[
                    UsernameIsTooLongException
                    | UsernameIsTooShortException
                    | WrongUsernameFormatException
                    | WrongPasswordFormatException
                    | WrongEmailFormatException
                    | PasswordDoesNotMatchException
                    | ValidationException
                ],
                examples=ExampleGenerator.create_bad_request_examples(
                    UsernameIsTooLongException,
                    UsernameIsTooShortException,
                    WrongUsernameFormatException,
                    WrongPasswordFormatException,
                    WrongEmailFormatException,
                    PasswordDoesNotMatchException,
                    LitestarValidationException,
                ),
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
    async def register(
        self,
        di_container: AsyncContainer,
        request: Request,
        data: user_requests.UserCreate = Body(),
    ) -> CreateUserResponseSchema:
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
        summary="Login with email and get access and refresh token pair.",
        description="Login with email and get access and refresh token pair. "
        "Email and password must be provided. "
        "Access token is returned in the response body. "
        "Refresh token is set into the cookie. "
        "Session will be created.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="User logged in",
                data_container=Response,
                examples=[
                    Example(
                        value={"access_token": "token"},
                        summary="Access token",
                    )
                ],
            ),
            status.HTTP_400_BAD_REQUEST: ResponseSpec(
                description="Wrong format of email address",
                data_container=ErrorResponse[ValidationException],
                examples=ExampleGenerator.create_bad_request_examples(
                    LitestarValidationException,
                ),
            ),
            status.HTTP_404_NOT_FOUND: ResponseSpec(
                description="User not found",
                data_container=ErrorResponse[UserDoesNotExistException],
                examples=ExampleGenerator.create_not_found_examples(
                    UserDoesNotExistException
                ),
            ),
            status.HTTP_409_CONFLICT: ResponseSpec(
                description="Given password is not valid",
                data_container=ErrorResponse[PasswordIsInvalidException],
                examples=ExampleGenerator.create_conflict_examples(
                    PasswordIsInvalidException
                ),
            ),
            **SERVER_ERROR_RESPONSES,
        },
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
                email=data.email,
                password=data.password,
                request=request,
                response=response,
            )

            tokens, *_ = await command_handler.handle_command(command)

            response.content = {"access_token": tokens.access_token}
            response.status_code = status.HTTP_200_OK

            return response

    @route(
        path="/refresh",
        http_method=[HttpMethod.POST],
        security=[{"BearerToken": []}],
        summary="Login with email and get access and refresh token pair.",
        description="Refresh token pair with refresh token from cookie. "
        "Access token is returned in the response body. "
        "Refresh token is set into the cookie.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Tokens successfully refreshed",
                data_container=Response,
                examples=[
                    Example(
                        value={"access_token": "token"},
                        summary="Access token",
                    )
                ],
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
    )
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
            response.status_code = status.HTTP_200_OK

            return response

    @route(
        path="/logout",
        http_method=[HttpMethod.POST],
        security=[{"BearerToken": []}],
        summary="Logout user",
        description="Logout user. "
        "Refresh token is removed from cookie. "
        "Session will be deactivated. "
        "Current user_id will be added to blacklist as a key and logout timestamp as a value.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="User logged out",
                data_container=Response,
                examples=[
                    Example(
                        value={"message": "Successfully logged out"},
                        summary="Message",
                    )
                ],
            ),
            **COMMON_RESPONSES,
            **SERVER_ERROR_RESPONSES,
        },
    )
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
            response.status_code = status.HTTP_200_OK

            return response

    @route(
        path="/password-reset/request",
        http_method=[HttpMethod.POST],
        summary="Request password reset",
        description="Request password reset with email. "
        "User must provide valid email address connected to his account. "
        "Email of password reset will be sent to user with generated token for operation confirmation.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Email of password reset has been sent",
                data_container=Response,
                examples=[
                    Example(
                        value={"message": "Email of password reset has been sent"},
                        summary="Message",
                    )
                ],
            ),
            status.HTTP_404_NOT_FOUND: ResponseSpec(
                description="User not found",
                data_container=ErrorResponse[UserDoesNotExistException],
                examples=ExampleGenerator.create_not_found_examples(
                    UserDoesNotExistException
                ),
            ),
            status.HTTP_400_BAD_REQUEST: ResponseSpec(
                description="Wrong format of email address",
                data_container=ErrorResponse[ValidationException],
                examples=ExampleGenerator.create_bad_request_examples(
                    LitestarValidationException,
                ),
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
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
            response.status_code = status.HTTP_200_OK

            return response

    @route(
        path="/password-reset/confirm",
        http_method=[HttpMethod.POST],
        summary="Confirm password reset",
        description="Confirm password reset with valid token and new password. "
        "Front-end must provide token and new password. "
        "Token must be valid. User credentials will be found from token as key.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Password successfully has been reset",
                data_container=Response,
                examples=[
                    Example(
                        value={"message": "Password successfully has been reset"},
                        summary="Message",
                    )
                ],
            ),
            status.HTTP_404_NOT_FOUND: ResponseSpec(
                description="Password token expired or unexpected user not found",
                data_container=ErrorResponse[
                    UserDoesNotExistException | PasswordTokenExpiredException
                ],
                examples=ExampleGenerator.create_not_found_examples(
                    PasswordTokenExpiredException, UserDoesNotExistException
                ),
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
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

    @route(
        path="/email-change/request",
        http_method=[HttpMethod.POST],
        summary="Request email change",
        description="Request to change user email. "
        "Valid email address must be provided. "
        "Email of email change will be sent to user with generated token for operation confirmation.",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Notification of email change has been sent",
                data_container=Response,
                examples=[
                    Example(
                        value={"message": "Notification of email change has been sent"},
                        summary="Message",
                    )
                ],
            ),
            status.HTTP_404_NOT_FOUND: ResponseSpec(
                description="User not found",
                data_container=ErrorResponse[UserDoesNotExistException],
                examples=ExampleGenerator.create_not_found_examples(
                    UserDoesNotExistException
                ),
            ),
            status.HTTP_400_BAD_REQUEST: ResponseSpec(
                description="Wrong format of email address",
                data_container=ErrorResponse[ValidationException],
                examples=ExampleGenerator.create_bad_request_examples(
                    LitestarValidationException,
                ),
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
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
            response.status_code = status.HTTP_200_OK

            return response

    @route(
        path="/email-change/confirm",
        http_method=[HttpMethod.POST],
        summary="Confirm email change",
        description="Confirm email change with valid token and new email. "
        "Front-end must provide token and new email. ",
        responses={
            status.HTTP_200_OK: ResponseSpec(
                description="Email successfully has been changed",
                data_container=Response,
                examples=[
                    Example(
                        value={"message": "Email successfully has been changed"},
                        summary="Message",
                    )
                ],
            ),
            status.HTTP_404_NOT_FOUND: ResponseSpec(
                description="Email token expired or unexpected user not found",
                data_container=ErrorResponse[
                    UserDoesNotExistException | EmailTokenExpiredException
                ],
                examples=ExampleGenerator.create_not_found_examples(
                    EmailTokenExpiredException, UserDoesNotExistException
                ),
            ),
            **SERVER_ERROR_RESPONSES,
        },
    )
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
            response.status_code = status.HTTP_200_OK

            return response
