from litestar import Controller, post, get, Request, Response, route, HttpMethod
from litestar.params import Body
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from dishka.integrations.base import FromDishka as Depends
from dishka.integrations.litestar import inject

# from src.schemas.request.user import UserLogin
#
# # from src.services.auth_service import AuthService
# import src.api.v1.utils as utils


# class AuthController(Controller):
#     path = "/auth"
#
#     @route(path="/login", http_method=[HttpMethod.POST])
#     # @inject
#     async def login(
#         self,
#         request: Request,
#         # auth_service: Depends[AuthService],
#         data: UserLogin = Body(
#             description="Login with email and get refresh tokens", title="UserLogin"
#         ),
#     ) -> dict:
#         client_info = utils.extract_client_info(request)
#         # result = await auth_service.login(data.username_or_email, data.password, client_info)
#
#         return client_info

#
# @post("/register")
# async def register(
#         self,
#         request: Request,
#         data: RegisterRequest = Body(),
#         auth_service: AuthService = Depends(get_auth_service)
# ):
#     # Validate password complexity
#     if not RegisterRequest.validate_password(data.password):
#         raise HTTPException(
#             status_code=HTTP_400_BAD_REQUEST,
#             detail="Password must be at least 8 characters and include uppercase, lowercase, and numbers"
#         )
#
#     client_info = extract_client_info(request)
#     success, result, error = await auth_service.register(
#         data.username, data.email, data.password, client_info
#     )
#
#     if not success:
#         raise HTTPException(
#             status_code=HTTP_400_BAD_REQUEST,
#             detail=error
#         )
#
#     return result
#
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
