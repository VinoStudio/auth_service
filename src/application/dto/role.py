from typing import List

from src.application.base.dto.dto import DTO
from dataclasses import dataclass


@dataclass(frozen=True)
class RoleCreation(DTO):
    name: str
    description: str
    security_level: int
    permissions: List[str]
