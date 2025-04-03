from datetime import datetime
from pydantic import BaseModel

import src.domain as domain

class CreateUserResponseSchema(BaseModel):
    user_id: str
    username: str
    created_at: datetime
    is_deleted: datetime | None

    @classmethod
    def from_entity(cls, user: domain.User):
        return cls(
            user_id=user.id.to_raw(),
            username=user.username.to_raw(),
            created_at=user.created_at,
            is_deleted=user.deleted_at,
        )