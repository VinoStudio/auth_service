from pydantic import BaseModel


class PermissionCreateRequestSchema(BaseModel):
    name: str
