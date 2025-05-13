from datetime import datetime

from pydantic import BaseModel


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime
    user_id: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str
