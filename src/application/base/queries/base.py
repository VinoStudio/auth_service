from dataclasses import dataclass, field
from uuid import uuid4, UUID
from abc import ABC
from typing import Generic, TypeVar, Any


@dataclass(frozen=True)
class BaseQuery(ABC): ...
