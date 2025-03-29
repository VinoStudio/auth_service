from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from src.infrastructure.base.message_broker.base import MessageBroker
from dataclasses import dataclass
from aiokafka import AIOKafkaProducer


@dataclass
class AsyncMessageProducer(MessageBroker):
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
