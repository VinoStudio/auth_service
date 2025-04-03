from dataclasses import asdict

import orjson

from src.infrastructure.message_broker.events import IntegrationEvent


def convert_event_to_broker_message(event: IntegrationEvent) -> bytes:
    return orjson.dumps(event)


# def convert_event_to_json(event: BaseEvent) -> dict[str, any]:
#     return asdict(event)

# AuthEvents = UserRegisterd
#
#
# def convert_consumer_message_to_event(message: dict) -> object:
#     match message.get("type"):
#         case "UserRegistered":
#             convert_user_registered_to_handler(**message)
#         case "UserDeleted":
#             convert_user_deleted_to_handler(**message)
#         case "UserUpdated":
#             convert_user_updated_to_handler(**message)
