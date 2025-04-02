from dataclasses import dataclass
from abc import ABC


@dataclass(frozen=True)
class BaseCommand(ABC):
    pass
