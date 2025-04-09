from dataclasses import dataclass
from typing import TypeVar


@dataclass(frozen=True)
class ExternalEvent: ...


EventType = TypeVar("EventType", bound=type[ExternalEvent])
