from dataclasses import dataclass, field
from typing import Dict


@dataclass
class MockResponse:
    cookies: Dict[str, str] = field(default_factory=dict)

    def set_cookie(self, key: str, value: str, **kwargs) -> None:
        self.cookies[key] = value
