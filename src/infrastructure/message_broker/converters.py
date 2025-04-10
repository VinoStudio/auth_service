from dataclasses import asdict

import orjson

from src.infrastructure.message_broker.events import IntegrationEvent
from src.infrastructure.message_broker.events.external.base import ExternalEvent
from src.infrastructure.message_broker.events.external.user_created import UserCreated
from src.infrastructure.message_broker.exceptions import MappingException


def convert_event_to_broker_message(event: IntegrationEvent) -> bytes:
    return orjson.dumps(event)


def convert_external_event_to_user_created_handler(
    event: dict[str, any],
) -> ExternalEvent:
    return UserCreated(
        user_id=event.get("user_id"),
        username=event.get("username"),
    )


def convert_external_event_to_event_command(event: dict[str, any]) -> ExternalEvent:
    match event.get("event_type"):
        case "UserCreated":
            return convert_external_event_to_user_created_handler(event)
        case _:
            raise MappingException(event.get("event_type"))
