from typing import Any, Dict, Optional, List, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import orjson
from src.infrastructure.repositories.user.user_writer import UserWriter
from src.infrastructure.db.uow import SQLAlchemyUoW
from src.infrastructure.base.message_broker.consumer import AsyncMessageConsumer
from dataclasses import dataclass
from aiokafka import AIOKafkaConsumer


@dataclass
class AsyncKafkaConsumer(AsyncMessageConsumer):
    session_factory: async_sessionmaker[AsyncSession]
    consumer: AIOKafkaConsumer
    running: bool = False

    async def start(self) -> None:
        """Start the consumer."""
        await self.consumer.start()
        self.running = True

    async def close(self) -> None:
        """Close the consumer."""
        await self.consumer.stop()

    async def subscribe(self, topics: List[str]) -> None:
        """Subscribe to one or more topics."""
        self.consumer.subscribe(topics=topics)

    async def start_consuming(self):
        """Start consuming messages."""
        try:
            async for message in self.consumer:
                if not self.running:
                    break

                try:
                    # Process the message
                    value = orjson.loads(message.value)
                    user_id = value.get("user_id")
                    event_type = value.get("type")

                    # Process different event types
                    if event_type == "USERNAME_UPDATED":
                        await self._handle_username_updated(user_id, value)
                    elif event_type == "USER_CREATED":
                        await self._handle_user_created(value)
                    elif event_type == "USER_DELETED":
                        await self._handle_user_deleted(user_id)
                    else:
                        raise ValueError(
                            f"Unknown event type: {event_type}"
                        )  # Commit the offset after processing
                    await self.consumer.commit()
                except Exception as e:
                    print(e)
        except Exception as e:
            self.running = False
            raise

    async def stop_consuming(self) -> None:
        """Stop consuming messages."""
        self.consumer.unsubscribe()

    @property
    def is_connected(self) -> bool:
        if not self.consumer:
            return False

        if getattr(self.consumer, "_closed", True):
            return False

        return True
