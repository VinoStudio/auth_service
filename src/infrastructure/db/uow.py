from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass

from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.exceptions.database import (
    CommitErrorException,
    RollbackErrorException,
)


@dataclass
class SQLAlchemyUoW(UnitOfWork):
    _session: AsyncSession

    async def commit(self) -> None:
        try:
            await self._session.commit()
        except SQLAlchemyError as error:
            raise CommitErrorException from error

    async def rollback(self) -> None:
        try:
            await self._session.rollback()
        except SQLAlchemyError as error:
            raise RollbackErrorException from error
