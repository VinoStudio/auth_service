from dishka import Provider, Scope, provide

from src.application.services.tasks.notification_manager import NotificationManager
from src.settings import Config


class NotificationManagerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_notification_manager(self, config: Config) -> NotificationManager:
        return NotificationManager(
            notification_email=config.smtp.user,
        )
