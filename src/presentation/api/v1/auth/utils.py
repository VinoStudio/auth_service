from typing import Dict, Any
from litestar import Request
from user_agents import parse
import orjson


# def extract_client_info(request: Request) -> Dict[str, Any]:
#     """Extract client information from request"""
#     client_host = request.client.host if request.client else "unknown"
#
#     user_agent = request.headers.get("User-Agent", "")
#     headers = dict(request.headers)
#
#     # Extract device/browser info from user agent (simplified)
#     device_info = {
#         "user_agent": user_agent,
#         "is_mobile": "mobile" in user_agent.lower() or "android" in user_agent.lower(),
#     }
#
#     return {
#         "ip_address": client_host,
#         "user_agent": user_agent,
#         "device_info": {
#             **device_info,
#             "headers": {
#                 k: v
#                 for k, v in headers.items()
#                 if k.lower() in ["x-forwarded-for", "accept-language", "referer"]
#             },
#         },
#     }


def extract_client_info(request: Request) -> Dict[str, Any]:
    client_host = request.client.host if request.client else None
    user_agent_string = request.headers.get("user-agent", "")

    # Parse user agent for device information
    ua = parse(user_agent_string)

    # Create a shorter representation of user agent
    browser = f"{ua.browser.family} {ua.browser.version_string}"
    os = f"{ua.os.family} {ua.os.version_string}"

    # Create simplified user agent string (limit to 100 chars)
    simplified_ua = f"{browser} on {os}"[:100]

    # Create device info JSON
    device_info = {
        "browser": browser,
        "os": os,
        "is_mobile": ua.is_mobile,
        "is_tablet": ua.is_tablet,
        "is_pc": ua.is_pc,
        "device": ua.device.family,
    }

    device_info_str = orjson.dumps(device_info)[:100]  # Limit to 100 chars

    return {
        "ip_address": client_host,
        "user_agent": simplified_ua,
        "device_info": device_info_str,
    }


#
# class JWTBearer:
#     def __init__(self, auto_error: bool = True):
#         self.auto_error = auto_error
#         self.security = HTTPBearer(auto_error=auto_error)
#
#     async def __call__(self, request: Request) -> Optional[Dict[str, Any]]:
#         try:
#             # Пробуем получить токен из заголовка Authorization
#             try:
#                 credentials = await self.security(request)
#                 session = credentials.credentials
#             except HTTPException:
#                 # Если нет в заголовке, смотрим в куках
#                 session = request.cookies.get("access_token")
#
#                 # Проверяем, не пытается ли кто-то использовать refresh_token
#                 if not session and request.cookies.get("refresh_token"):
#                     raise HTTPException(
#                         status_code=status.HTTP_403_FORBIDDEN,
#                         detail="Refresh session cannot be used for API access",
#                     )
#
#             if not session:
#                 if self.auto_error:
#                     raise HTTPException(
#                         status_code=status.HTTP_403_FORBIDDEN,
#                         detail="No authentication session provided",
#                     )
#                 return None
#
#             # Проверяем валидность токена
#             payload = self.verify_jwt(session)
#
#             # Проверяем, не был ли пользователь разлогинен после выпуска токена
#             user_id = payload.get("sub")
#             token_issued_at = payload.get("iat", 0)
#
#             # Проверяем время выхода из системы в Redis
#             logout_time = redis_client.get(f"logout:{user_id}")
#             if logout_time and float(logout_time) > token_issued_at:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="Token was issued before logout. Please login again.",
#                 )
#
#             # Сохраняем информацию о пользователе в request
#             request.state.user = payload
#             return payload
#
#         except JWTError:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Invalid session or expired session",
#             )
#
#     def verify_jwt(self, session: str) -> dict:
#         try:
#             payload = jwt.decode(session, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
#
#             # Проверяем срок действия
#             if payload.get("exp"):
#                 expiration = datetime.fromtimestamp(payload.get("exp"))
#                 if datetime.utcnow() > expiration:
#                     raise HTTPException(
#                         status_code=status.HTTP_403_FORBIDDEN,
#                         detail="Token has expired",
#                     )
#
#             return payload
#         except JWTError:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN, detail="Invalid session"
#             )
