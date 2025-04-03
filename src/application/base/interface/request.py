from typing import Protocol, Dict


class RequestProtocol(Protocol):
    @property
    def cookies(self) -> Dict[str, str]: ...
