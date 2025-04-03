from typing import Any, Dict, Optional, List, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import orjson

from src.application.base.event_publisher.event_dispatcher import BaseEventDispatcher
from src.application.event_handlers.event_dispatcher import EventDispatcher
from src.infrastructure.repositories.user.user_writer import UserWriter
from src.infrastructure.db.uow import SQLAlchemyUoW
from src.infrastructure.base.message_broker.consumer import AsyncMessageConsumer
from dataclasses import dataclass
from aiokafka import AIOKafkaConsumer


@dataclass
class AsyncKafkaConsumer(AsyncMessageConsumer):
    consumer: AIOKafkaConsumer
    event_dispatcher: BaseEventDispatcher
    running: bool = False

    async def start(self) -> None:
        await self.consumer.start()
        self.running = True

    async def close(self) -> None:
        await self.consumer.stop()

    async def subscribe(self, topics: List[str]) -> None:
        self.consumer.subscribe(topics=topics)

    async def start_consuming(self):
        try:
            async for message in self.consumer:
                if not self.running:
                    break

                try:
                    # Process message as before
                    event_data = orjson.loads(message.value)
                    event_command = c.convert_external_event_to_event_command(
                        event_data
                    )
                    await self.event_dispatcher.dispatch(event_command)
                    await self.consumer.commit()
                except Exception as e:
                    print(f"Error processing message: {e}")
                except Exception as e:
                    logging.error(f"Error processing message: {str(e)}")
        except Exception as e:
            self.running = False
            raise

    async def stop_consuming(self) -> None:
        self.consumer.unsubscribe()

    @property
    def is_connected(self) -> bool:
        if not self.consumer:
            return False
        if getattr(self.consumer, "_closed", True):
            return False
        return True
