from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

VT = TypeVar("VT", bound=Any)  # Generic type for single-value VOs


@dataclass(frozen=True, slots=True, eq=True, unsafe_hash=True)
class ValueObject(ABC, Generic[VT]):
    """Base class for Value Objects (immutable, validated, comparable)."""

    @abstractmethod
    def _validate(self) -> None:
        """Validate the object's state."""
        raise NotImplementedError

    def __post_init__(self) -> None:
        """Run validation after initialization."""
        self._validate()

    @abstractmethod
    def to_raw(self) -> str:
        """Convert the VO back to its raw form."""
        raise NotImplementedError
