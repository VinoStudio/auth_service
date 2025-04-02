from pydantic import BaseModel, EmailStr, model_validator, Field
from typing import Optional


class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: datetime
    iat: datetime = Field(default_factory=datetime.utcnow)
    jti: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scope: list[str] = []  # permissions