from abc import ABC, abstractmethod
from dataclasses import dataclass

from aiokafka import AIOKafkaProducer

from src.infrastructure.base.message_broker.base import MessageBroker


@dataclass
class AsyncMessageProducer(MessageBroker, ABC):
    producer: AIOKafkaProducer

    @abstractmethod
    async def publish(self, topic: str, message: bytes, key: bytes | None) -> None:
        """Publish a message to a topic."""
        raise NotImplementedError

    @abstractmethod
    async def start(self) -> None:
        """Start the producer."""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Close the producer."""
        raise NotImplementedError
