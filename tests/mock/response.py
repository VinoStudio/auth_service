from dataclasses import dataclass, field


@dataclass
class MockResponse:
    cookies: dict[str, str] = field(default_factory=dict)

    def set_cookie(self, key: str, value: str, **kwargs) -> None:
        self.cookies[key] = value
