from dataclasses import dataclass
from abc import ABC
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class BaseRepository(ABC): ...


class BaseMemoryRepository(BaseRepository):
    pass


@dataclass
class SQLAlchemyRepository(BaseRepository):
    _session: AsyncSession
