from pydantic import BaseModel, EmailStr, model_validator, Field
from typing import Optional
from uuid6 import uuid7
import re

#PASSWORD_PATTERN = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    repeat_password: str = Field(..., min_length=8, max_length=100)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)

    @model_validator(mode="after")
    def validate_password(self) -> "UserCreate":
        if self.password != self.repeat_password:
            raise ValueError("Passwords do not match")

        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLogout(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str
