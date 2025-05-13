from dataclasses import dataclass

from src.application.base.dto.dto import DTO


@dataclass(frozen=True)
class RoleCreation(DTO):
    name: str
    description: str
    security_level: int
    permissions: list[str]
