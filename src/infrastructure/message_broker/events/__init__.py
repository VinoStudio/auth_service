from src.infrastructure.message_broker.events.base import IntegrationEvent
from src.infrastructure.message_broker.events.user_registered import UserRegistered

__all__ = (
    "IntegrationEvent",
    "UserRegistered",
)
