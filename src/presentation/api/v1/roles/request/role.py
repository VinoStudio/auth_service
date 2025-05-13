
from pydantic import BaseModel, Field


class RoleCreateRequestSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=35)
    description: str = Field(..., max_length=100)
    security_level: int = 8
    permissions: list[str] = Field(["project:view", "content:view"], min_length=1)


class RoleDeleteRequestSchema(BaseModel):
    role_name: str


class RoleAssignRequestSchema(BaseModel):
    role_name: str


class RoleRemoveRequestSchema(BaseModel):
    role_name: str


class RoleUpdateRequestSchema(BaseModel):
    description: str | None = Field(None, min_length=3, max_length=100)
    security_level: int | None = Field(None, ge=0, le=10)
    permissions: list[str] | None = Field(
        None, min_length=1, examples=["user:read", "project:view", "content:view"]
    )


class RemoveRolePermissionsRequestSchema(BaseModel):
    permissions: list[str] = Field(
        examples=["user:read", "project:view", "content:view"], min_length=1
    )
