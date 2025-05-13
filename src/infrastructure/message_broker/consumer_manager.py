import asyncio
from collections import defaultdict
from dataclasses import dataclass, field

from src.infrastructure.base.message_broker.consumer import AsyncMessageConsumer


@dataclass
class KafkaConsumerManager:
    consumers: dict[str, AsyncMessageConsumer] = field(
        default_factory=dict, kw_only=True
    )
    # Track the number of consumers per topic
    _consumer_count: dict[str, int] = field(
        default_factory=lambda: defaultdict(int), kw_only=True
    )

    async def start_consumers(self) -> None:
        for consumer in self.consumers.values():
            await consumer.start()

    async def stop_consumers(self) -> None:
        for consumer in self.consumers.values():
            await consumer.close()

    def register_consumer(self, topic: str, consumer: AsyncMessageConsumer) -> None:
        # Create a unique key using topic and counter
        self._consumer_count[topic] += 1
        key = f"{topic}_{self._consumer_count[topic]}"
        self.consumers[key] = consumer

    async def start_consuming(self) -> None:
        await asyncio.gather(
            *[consumer.start_consuming() for consumer in self.consumers.values()]
        )

    async def stop_consuming(self) -> None:
        for consumer in self.consumers.values():
            await consumer.stop_consuming()

    @property
    def status(self) -> list[bool]:
        # Check the status of each consumer
        statuses = [consumer.is_connected for consumer in self.consumers.values()]
        return statuses
