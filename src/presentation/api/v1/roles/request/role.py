from blib2to3.pgen2.parse import Optional
from pydantic import BaseModel, Field
from typing import List


class RoleCreateRequestSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=35)
    description: str = Field(..., min_length=3, max_length=100)
    security_level: int = 8
    permissions: List[str] = Field(
        ["user:read", "project:view", "content:view"], min_length=1
    )


class RoleDeleteRequestSchema(BaseModel):
    role_name: str


class RoleAssignRequestSchema(BaseModel):
    role_name: str


class RoleRemoveRequestSchema(BaseModel):
    role_name: str


class RoleUpdateRequestSchema(BaseModel):
    description: Optional[str] = Field(None, min_length=3, max_length=100)
    security_level: Optional[int] = Field(None, ge=0, le=10)
    permissions: Optional[List[str]] = Field(
        None, min_length=1, examples=["user:read", "project:view", "content:view"]
    )


class RemoveRolePermissionsRequestSchema(BaseModel):
    permissions: List[str] = Field(
        examples=["user:read", "project:view", "content:view"], min_length=1
    )
