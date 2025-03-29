from dataclasses import dataclass, field
from src.infrastructure.base.message_broker.consumer import AsyncMessageConsumer
from typing import Dict, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

@dataclass
class KafkaConsumerManager(object):
    consumers: Dict[str, AsyncMessageConsumer] = field(default_factory=dict, kw_only=True)

    async def start_consumers(self) -> None:
        for consumer in self.consumers.values():
            await consumer.start()

    async def stop_consumers(self) -> None:
        for consumer in self.consumers.values():
            await consumer.close()

    async def register_consumer(self, topic: str, consumer: AsyncMessageConsumer) -> None:
        self.consumers[topic] = consumer

    async def start_consuming(self):
        for consumer in self.consumers.values():
            await consumer.start_consuming()