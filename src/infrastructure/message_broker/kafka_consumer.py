from dataclasses import dataclass

import orjson
import structlog
from aiokafka import AIOKafkaConsumer

import src.infrastructure.message_broker.converters as c
from src.application.base.event_sourcing.event_consumer import BaseEventConsumer
from src.infrastructure.base.message_broker.consumer import AsyncMessageConsumer

logger = structlog.getLogger(__name__)


@dataclass
class AsyncKafkaConsumer(AsyncMessageConsumer):
    consumer: AIOKafkaConsumer
    event_consumer: BaseEventConsumer
    running: bool = False

    async def start(self) -> None:
        await self.consumer.start()
        self.running = True
        logger.debug("Consumer started", status=self.running)

    async def close(self) -> None:
        await self.consumer.stop()
        self.running = False
        logger.debug("Consumer stopped", status=self.running)

    async def subscribe(self, topics: list[str]) -> None:
        self.consumer.subscribe(topics=topics)
        logger.debug("Subscribed to topics", topics=topics)

    async def start_consuming(self) -> None:
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                try:
                    event_data = orjson.loads(message.value)
                    logger.info("Received message", message=event_data)
                    event_command = c.convert_external_event_to_event_command(
                        event_data
                    )
                    logger.info("Event command", event_command=event_command)
                    await self.event_consumer.handle(event_command)
                    await self.consumer.commit()

                except (orjson.JSONDecodeError, ValueError) as e:
                    logger.error("Invalid message format", error=str(e))
                    continue
                except RuntimeError as e:
                    logger.error("Event processing failed", error=str(e))
                    continue
        except Exception:
            self.running = False
            raise

    async def stop_consuming(self) -> None:
        self.consumer.unsubscribe()
        logger.debug("Unsubscribed from topics")

    @property
    def is_connected(self) -> bool:
        if not self.consumer:
            return False
        return not getattr(self.consumer, "_closed", True)
