from typing import Protocol


class RequestProtocol(Protocol):
    @property
    def cookies(self) -> dict[str, str]: ...
