from litestar import Controller, Request, Response, route, HttpMethod
from litestar.di import Provide
from litestar.params import Body
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST
from dishka import AsyncContainer

from src.application.base.mediator.command import BaseCommandMediator
from src.application.cqrs.user.commands import RegisterUserCommand, LoginUserCommand
from src.application.dependency_injector.di import get_container
from src.presentation.api.v1.auth.request.user import UserLogin, UserCreate
from src.presentation.api.v1.auth.response.user import (
    CreateUserResponseSchema,
)


class AuthController(Controller):
    path = "/auth"
    tags = ["Auth"]
    dependencies = {"di_container": Provide(get_container)}

    @route(path="/register", http_method=[HttpMethod.POST], sync_to_thread=False)
    async def register(
        self, di_container: AsyncContainer, request: Request, data: UserCreate = Body()
    ) -> CreateUserResponseSchema:

        try:
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
        except Exception as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))

    @route(path="/login", http_method=[HttpMethod.POST], sync_to_thread=False)
    async def login(
        self,
        di_container: AsyncContainer,
        request: Request,
        data: UserLogin = Body(
            description="Login with email and get refresh tokens", title="UserLogin"
        ),
    ) -> Response:
        try:
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

                response.content = tokens
                response.headers["Authorization"] = "Bearer"
                response.headers["Access-Token"] = tokens.access_token

                return response

        except Exception as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


# @post("/refresh")
# async def refresh_token(
#         self,
#         request: Request,
#         data: RefreshTokenRequest = Body(),
#         auth_service: AuthService = Depends(get_auth_service)
# ):
#     client_info = extract_client_info(request)
#     result = await auth_service.refresh_token(data.refresh_token, client_info)
#
#     if not result:
#         raise HTTPException(
#             status_code=HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired refresh session"
#         )
#
#     return result
#
# @post("/logout")
# async def logout(
#         self,
#         request: Request,
#         auth_service: AuthService = Depends(get_auth_service)
# ):
#     auth_header = request.headers.get("Authorization", "")
#     if not auth_header.startswith("Bearer "):
#         raise HTTPException(
#             status_code=HTTP_401_UNAUTHORIZED,
#             detail="Missing or invalid session"
#         )
#
#     session = auth_header.replace("Bearer ", "")
#     success = await auth_service.logout(session)
#
#     if not success:
#         raise HTTPException(
#             status_code=HTTP_401_UNAUTHORIZED,
#             detail="Invalid session"
#         )
#
#     return {"message": "Successfully logged out"}
