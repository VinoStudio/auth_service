from typing import List

from src.application.base.dto.dto import DTO
from dataclasses import dataclass

@dataclass(frozen=True)
class PermissionCreation(DTO):
    name: str
