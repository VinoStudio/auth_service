import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine
from src.application.dependency_injector.di import get_container
from litestar import Litestar
from aiojobs import Scheduler

from src.infrastructure.message_broker.consumer_manager import KafkaConsumerManager
from src.presentation.api.base_role_permissions_setup import seed_roles_and_permissions
from src.infrastructure.db.models.base import BaseModel
from src.infrastructure.message_broker.kafka_consumer import AsyncKafkaConsumer
from aiokafka import AIOKafkaConsumer
from src.infrastructure.base.message_broker.producer import AsyncMessageProducer
from src.infrastructure.log.main import configure_logging
from src.settings.config import Config, get_config
from src.presentation.api.kafka_setup import create_topic_with_partitions
import structlog


logger = structlog.getLogger(__name__)

config: Config = get_config()


async def init_message_broker():
    container = get_container()
    producer = await container.get(AsyncMessageProducer)
    await producer.start()

    logger.info("Message broker initialized")


async def close_message_broker():
    container = get_container()
    producer = await container.get(AsyncMessageProducer)
    await producer.close()

    logger.info("Message broker closed")


async def start_kafka_consumers():
    container = get_container()
    consumer_manager = await container.get(KafkaConsumerManager)
    await consumer_manager.start_consumers()

    print("Starting kafka consumer", consumer_manager.status)


async def stop_kafka_consumers():
    container = get_container()
    consumer_manager = await container.get(KafkaConsumerManager)

    await consumer_manager.stop_consuming()
    await consumer_manager.stop_consumers()
    print("Stopping kafka consumer", consumer_manager.status)


async def consume_in_background():
    container = get_container()
    consumer_manager = await container.get(KafkaConsumerManager)

    await consumer_manager.start_consuming()


async def create_tables():
    container = get_container()
    engine = await container.get(AsyncEngine)
    async with engine.begin() as e:
        await e.run_sync(BaseModel.metadata.create_all)


async def dispose_engine():
    container = get_container()
    engine = await container.get(AsyncEngine)
    async with engine.begin() as e:
        await e.run_sync(BaseModel.metadata.drop_all)
    await engine.dispose()


@asynccontextmanager
async def lifespan(app: Litestar):
    create_topic_with_partitions()
    configure_logging()

    await create_tables()
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
