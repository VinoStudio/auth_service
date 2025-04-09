from src.infrastructure.base.message_broker.producer import AsyncMessageProducer
from dataclasses import dataclass
import structlog

logger = structlog.getLogger(__name__)


@dataclass
class AsyncKafkaProducer(AsyncMessageProducer):

    async def publish(self, topic: str, value: bytes, key: bytes | None) -> None:
        """Publish a message to a topic."""
        await self.producer.send(topic=topic, value=value, key=key)
        logger.debug("Message published", topic=topic, value=value)

    async def start(self) -> None:
        """Start the producer."""
        await self.producer.start()
        logger.debug("Producer started")

    async def close(self) -> None:
        """Close the producer."""
        await self.producer.stop()
        logger.debug("Producer closed")

    @property
    def is_connected(self) -> bool:
        if not self.producer:
            return False

        if getattr(self.producer, "_closed", True):
            return False

        return True
