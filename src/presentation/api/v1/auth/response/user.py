from datetime import datetime
from typing import Self

from pydantic import BaseModel

from src import domain


class CreateUserResponseSchema(BaseModel):
    user_id: str
    username: str
    created_at: datetime
    is_deleted: datetime | None

    @classmethod
    def from_entity(cls, user: domain.User) -> Self:
        return cls(
            user_id=user.id.to_raw(),
            username=user.username.to_raw(),
            created_at=user.created_at,
            is_deleted=user.deleted_at,
        )
