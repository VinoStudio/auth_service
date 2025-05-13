from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Union

VT = TypeVar("VT", bound=Any)  # Generic type for single-value VOs
MT = TypeVar("MT", bound=Any)  # Generic type for multi-value VOs


@dataclass(frozen=True, slots=True, eq=True, unsafe_hash=True)
class ValueObject(ABC, Generic[VT, MT]):
    """Base class for Value Objects (immutable, validated, comparable)."""

    @abstractmethod
    def _validate(self) -> None:
        """Validate the object's state."""
        raise NotImplementedError

    def __post_init__(self) -> None:
        """Run validation after initialization."""
        self._validate()

    @abstractmethod
    def to_raw(self) -> Union[VT, MT]:
        """Convert the VO back to its raw form."""
        raise NotImplementedError
