from src.infrastructure.base.message_broker.producer import AsyncMessageProducer
from dataclasses import dataclass


@dataclass
class AsyncKafkaProducer(AsyncMessageProducer):

    async def publish(self, topic: str, message: bytes, key: bytes | None) -> None:
        """Publish a message to a topic."""
        await self.producer.send(topic, value=message, key=key)

    async def start(self) -> None:
        """Start the producer."""
        await self.producer.start()

    async def close(self) -> None:
        """Close the producer."""
        await self.producer.stop()

    @property
    def is_connected(self) -> bool:
        if not self.producer:
            return False

        if getattr(self.producer, "_closed", True):
            return False

        return True
