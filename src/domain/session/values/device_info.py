from dataclasses import dataclass
from typing import Self, Union

import orjson

from src.domain.base.values.base import ValueObject


@dataclass(frozen=True)
class DeviceInfo(ValueObject):
    browser_family: str
    os_family: str
    device: str
    accept_lang: str
    accept_encoding: str

    @classmethod
    def create(cls, device_info: bytes) -> Self:
        return cls(**orjson.loads(device_info))

    def to_bytes(self) -> bytes:
        return orjson.dumps(self.__dict__)

    def _validate(self) -> None: ...

    def to_raw(self) -> str:
        return f"{self.browser_family} on {self.os_family}- {self.device}"
