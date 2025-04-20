from pydantic import BaseModel, Field
from typing import List


class PermissionCreateRequestSchema(BaseModel):
    name: str
