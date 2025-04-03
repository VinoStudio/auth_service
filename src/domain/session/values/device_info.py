from src.domain.base.values.base import BaseValueObject
from dataclasses import dataclass
from typing import Self
import orjson


@dataclass(frozen=True)
class DeviceInfo(BaseValueObject):
    browser_family: str
    browser_version: str
    os_family: str
    os_version: str
    device: str
    accept_lang: str
    accept_encoding: str

    @classmethod
    def create(cls, device_info: bytes) -> Self:
        return cls(**orjson.loads(device_info))

    def to_bytes(self):
        return orjson.dumps(self.__dict__)

    def _validate(self): ...

    def __str__(self) -> str:
        return f"{self.browser_family} {self.browser_version} on {self.os_family} {self.os_version} - {self.device}"
