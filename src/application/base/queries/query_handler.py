from application.base.queries.base import BaseQuery
from abc import ABC
from typing import Generic, TypeVar, Any
from dataclasses import dataclass

QT = TypeVar("QT", bound=type(BaseQuery))
QR = TypeVar("QR", bound=Any)


@dataclass(frozen=True)
class BaseQueryHandler(ABC, Generic[QT, QR]):
    async def handle(self, query: QT) -> QR: ...
