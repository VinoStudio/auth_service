from dataclasses import dataclass

from src.application.base.dto.dto import DTO


@dataclass(frozen=True)
class PermissionCreation(DTO):
    name: str
