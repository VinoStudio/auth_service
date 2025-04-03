from dishka import provide, Provider, Scope, decorate

from src.application.base.event_publisher.event_dispatcher import BaseEventDispatcher
from src.infrastructure.base.message_broker.producer import AsyncMessageProducer
from src.infrastructure.base.message_broker.consumer import AsyncMessageConsumer
from src.settings.config import Config
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from src.infrastructure.message_broker.kafka_producer import AsyncKafkaProducer
from src.infrastructure.message_broker.kafka_consumer import AsyncKafkaConsumer
from src.infrastructure.message_broker.consumer_manager import KafkaConsumerManager
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class MessageBrokerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_message_producer(self, config: Config) -> AsyncMessageProducer:
        return AsyncKafkaProducer(
            producer=AIOKafkaProducer(bootstrap_servers=config.kafka.kafka_url),
        )


class KafkaConsumerManagerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_kafka_consumer_manager(self) -> KafkaConsumerManager:

        return KafkaConsumerManager()

    @decorate
    async def kafka_consumer_registry(
        self,
        event_dispatcher: BaseEventDispatcher,
        manager: KafkaConsumerManager,
    ) -> KafkaConsumerManager:
        user_topic_consumer_1 = AsyncKafkaConsumer(
            consumer=AIOKafkaConsumer(
                "user_topic",
                bootstrap_servers="localhost:9092",
                group_id="auth_group",
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
            ),
            event_dispatcher=event_dispatcher,
        )

        user_topic_consumer_2 = AsyncKafkaConsumer(
            consumer=AIOKafkaConsumer(
                "user_topic",
                bootstrap_servers="localhost:9092",
                group_id="auth_group",
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
            ),
            session_factory=session_factory,
        )

        await manager.register_consumer(
            topic="user_topic", consumer=user_topic_consumer_1
        )
        await manager.register_consumer(
            topic="user_topic", consumer=user_topic_consumer_2
        )

        return manager
