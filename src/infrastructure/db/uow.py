from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.base.uow import UnitOfWork
from src.infrastructure.exceptions.database import (
    CommitException,
    RollbackException,
)


@dataclass
class SQLAlchemyUoW(UnitOfWork):
    _session: AsyncSession

    async def commit(self) -> None:
        try:
            await self._session.commit()
        except SQLAlchemyError as error:
            raise CommitException from error

    async def rollback(self) -> None:
        try:
            await self._session.rollback()
        except SQLAlchemyError as error:
            raise RollbackException from error
