from dataclasses import dataclass, field


@dataclass
class MockRequest:
    cookies: dict[str, str] = field(default_factory=dict)

    def get_cookie(self, key: str) -> str | None:
        return self.cookies.get(key)

    def set_cookie(self, key: str, value: str, **kwargs) -> None:
        self.cookies[key] = value
