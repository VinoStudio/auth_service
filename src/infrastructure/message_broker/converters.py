# from dataclasses import asdict
#
# import orjson
#
# from src.domain.base.events.base import BaseEvent
#
#
# def convert_event_to_broker_message(event: BaseEvent) -> bytes:
#     return orjson.dumps(event)
#
#
# # def convert_event_to_json(event: BaseEvent) -> dict[str, any]:
# #     return asdict(event)
