from dataclasses import dataclass
from typing import Any

import src.infrastructure.message_broker.converters as c
import src.infrastructure.message_broker.events as integration_events
from src.application.base.events.event_handler import EventHandler


@dataclass(frozen=True)
class UserRegisteredEventHandler(EventHandler[integration_events.UserRegistered, Any]):
    async def handle(self, event: integration_events.UserRegistered) -> dict:
        return {
            "key": event.event_id.encode("utf-8"),
            "topic": event.topic,
            "value": c.convert_event_to_broker_message(event),
        }
