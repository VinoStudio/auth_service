from pydantic import BaseModel
from typing import List


class RoleCreateRequestSchema(BaseModel):
    name: str
    description: str
    security_level: int = 8
    permissions: List[str]
