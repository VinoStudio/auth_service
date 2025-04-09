from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class MockRequest:
    cookies: Dict[str, str] = field(default_factory=dict)

    def get_cookie(self, key: str) -> Optional[str]:
        return self.cookies.get(key)

    def set_cookie(self, key: str, value: str, **kwargs) -> None:
        self.cookies[key] = value
