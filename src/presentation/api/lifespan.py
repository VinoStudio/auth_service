from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from aiojobs import Scheduler
from litestar import Litestar
from sqlalchemy.ext.asyncio import AsyncEngine

from src.application.dependency_injector.di import get_container
from src.infrastructure.base.message_broker.producer import AsyncMessageProducer
from src.infrastructure.db.models.base import BaseModel
from src.infrastructure.log.main import configure_logging
from src.infrastructure.message_broker.consumer_manager import KafkaConsumerManager
from src.presentation.api.base_role_permissions_setup import seed_roles_and_permissions
from src.presentation.api.kafka_setup import create_kafka_topic
from src.settings.config import Config, get_config

logger = structlog.getLogger(__name__)

config: Config = get_config()


async def init_message_broker() -> None:
    container = get_container()
    producer = await container.get(AsyncMessageProducer)
    await producer.start()

    logger.info("Message broker initialized")


async def close_message_broker() -> None:
    container = get_container()
    producer = await container.get(AsyncMessageProducer)
    await producer.close()

    logger.info("Message broker closed")


async def start_kafka_consumers() -> None:
    container = get_container()
    consumer_manager = await container.get(KafkaConsumerManager)
    await consumer_manager.start_consumers()


async def stop_kafka_consumers() -> None:
    container = get_container()
    consumer_manager = await container.get(KafkaConsumerManager)

    await consumer_manager.stop_consuming()
    await consumer_manager.stop_consumers()


async def consume_in_background() -> None:
    container = get_container()
    consumer_manager = await container.get(KafkaConsumerManager)

    await consumer_manager.start_consuming()


# async def create_tables() -> None:
#     container = get_container()
#     engine = await container.get(AsyncEngine)
#     async with engine.begin() as e:
#         await e.run_sync(BaseModel.metadata.create_all)


async def dispose_engine() -> None:
    container = get_container()
    engine = await container.get(AsyncEngine)
    await engine.dispose()


@asynccontextmanager
async def lifespan(_app: Litestar) -> AsyncGenerator[None, None]:
    create_kafka_topic()
    configure_logging()

    await seed_roles_and_permissions()
    await init_message_broker()
    await start_kafka_consumers()

    container = get_container()
    scheduler = await container.get(Scheduler)
    job = await scheduler.spawn(consume_in_background())

    yield
    await job.close()
    await close_message_broker()
    await stop_kafka_consumers()
    await dispose_engine()
