from dataclasses import dataclass
from typing import Generic, TypeVar, Any
from abc import ABC, abstractmethod

VT = TypeVar("VT", bound=Any)


@dataclass(frozen=True)
class BaseValueObject(ABC):

    @abstractmethod
    def _validate(self):
        raise NotImplementedError

    def __post_init__(self):
        self._validate()


@dataclass(frozen=True)
class ValueObject(BaseValueObject, ABC, Generic[VT]):
    value: VT

    def to_raw(self) -> VT:
        return self.value
