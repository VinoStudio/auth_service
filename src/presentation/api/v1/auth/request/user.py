
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    repeat_password: str = Field(..., min_length=8, max_length=100)
    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)
    middle_name: str | None = Field(None, max_length=50)

    @field_validator("email")
    def lowercase_email(cls, value: str) -> str: # noqa
        return value.lower() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_password(self) -> "UserCreate":
        if self.password != self.repeat_password:
            raise ValueError("Passwords do not match")

        return self

    @model_validator(mode="after")
    def validate_names(self) -> "UserCreate":
        provided_names = [
            name
            for name in [self.first_name, self.last_name, self.middle_name]
            if name is not None
        ]

        if len(provided_names) != len(set(provided_names)) and len(provided_names) > 1:
            raise ValueError(
                "First name, last name, and middle name must be different from each other"
            )

        return self


class ResetRequest(BaseModel):
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLogout(BaseModel):
    refresh_token: str


class PasswordResetRequest(ResetRequest): ...


class EmailChangeRequest(ResetRequest): ...


class PasswordReset(BaseModel):
    token: str
    new_password: str


class EmailChange(BaseModel):
    token: str
    new_email: EmailStr


class DisconnectProvider(BaseModel):
    provider_name: str
    provider_user_id: str
