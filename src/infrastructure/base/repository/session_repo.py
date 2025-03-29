from abc import ABC
from typing import Dict, Any, List, Optional
import src.infrastructure.db.models as models


class BaseSessionRepository(ABC):
    async def create_user_session(
        self, user_id: str, user_info: Dict[str, Any]
    ) -> models.UserSession:
        raise NotImplementedError

    async def get_active_sessions(self, user_id: str) -> List[models.UserSession]:
        raise NotImplementedError

    async def deactivate_session(self, session_id: str) -> Optional[models.UserSession]:
        raise NotImplementedError

    async def deactivate_all_sessions(self, user_id: str) -> int:
        raise NotImplementedError

    async def update_session_activity(self, session_id: str) -> None:
        raise NotImplementedError
