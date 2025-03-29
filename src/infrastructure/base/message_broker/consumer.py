from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from src.infrastructure.base.message_broker.base import MessageBroker
from dataclasses import dataclass
from aiokafka import AIOKafkaConsumer


@dataclass
class AsyncMessageConsumer(MessageBroker):
    consumer: AIOKafkaConsumer

    @abstractmethod
    async def start(self) -> None:
        """Start the consumer."""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Close the consumer."""
        raise NotImplementedError

    @abstractmethod
    async def subscribe(self, topics: List[str]) -> None:
        """Subscribe to one or more topics."""
        raise NotImplementedError

    @abstractmethod
    async def start_consuming(self) -> None:
        """Start consuming messages."""
        raise NotImplementedError

    @abstractmethod
    async def stop_consuming(self) -> None:
        """Stop consuming messages."""
        raise NotImplementedError
