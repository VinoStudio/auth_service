from dataclasses import dataclass
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.application.base.events.external_event_handler import ExternalEventHandler
from src.application.services.tasks.notification_manager import NotificationManager
from src.infrastructure.message_broker.events.external.user_created import UserCreated
from src.infrastructure.repositories import UserReader

import src.domain as domain


@dataclass(frozen=True)
class UserCreatedEventHandler(ExternalEventHandler[UserCreated, None]):
    session_factory: async_sessionmaker
    notification_manager: NotificationManager

    async def handle(self, event: UserCreated) -> None:
        async with self.session_factory() as session:
            user_reader = UserReader(session)

            user: domain.User = await user_reader.get_user_by_id(event.user_id)

            await self.notification_manager.send_registration_notification(
                user.as_dict()
            )
