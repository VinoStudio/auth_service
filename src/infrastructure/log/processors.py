from collections.abc import Callable
from typing import Any

import orjson
import structlog

ProcessorType = Callable[
    [
        structlog.types.WrappedLogger,
        str,
        structlog.types.EventDict,
    ],
    str | bytes,
]


def serialize_to_json(data: Any) -> str:
    return orjson.dumps(data).decode()


def get_render_processor(
    render_json_logs: bool = False,
    serializer: Callable[..., str | bytes] = serialize_to_json,
    colors: bool = True,
) -> ProcessorType:
    if render_json_logs:
        return structlog.processors.JSONRenderer(serializer=serializer)
    return structlog.dev.ConsoleRenderer(
        colors=colors,
        pad_event=0,
        pad_level=False,
        event_key="event",
    )
