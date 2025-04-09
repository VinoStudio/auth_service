from typing import List

from src.application.base.dto.dto import DTO
from dataclasses import dataclass


@dataclass(frozen=True)
class RoleCreation(DTO):
    name: str
    description: str
    security_level: int
    permissions: List[str]

# class RoleUpdate(DTO):
#     role_name: str
#     new_role_name: str | None = None
#     new_security_level: int | None = None
#     new_description: str | None = None
#     new_permissions: List[str] | None = None