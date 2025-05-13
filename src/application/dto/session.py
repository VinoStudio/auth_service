from dataclasses import dataclass

from src.application.base.dto.dto import DTO


@dataclass(frozen=True)
class DeviceInformation(DTO):
    user_agent: str
    device_id: str
    device_info: bytes
