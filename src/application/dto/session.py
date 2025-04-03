from src.application.base.dto.dto import DTO
from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceInformation(DTO):
    user_agent: str
    device_id: str
    device_info: bytes