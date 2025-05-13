from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from dishka import Provider, Scope, decorate, provide

from src.application.base.event_sourcing.event_consumer import BaseEventConsumer
from src.infrastructure.base.message_broker.producer import AsyncMessageProducer
from src.infrastructure.message_broker.consumer_manager import KafkaConsumerManager
from src.infrastructure.message_broker.kafka_consumer import AsyncKafkaConsumer
from src.infrastructure.message_broker.kafka_producer import AsyncKafkaProducer
from src.settings.config import Config


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
        event_consumer: BaseEventConsumer,
        manager: KafkaConsumerManager,
        config: Config,
    ) -> KafkaConsumerManager:
        auth_consumer_1 = AsyncKafkaConsumer(
            consumer=AIOKafkaConsumer(
                "user_service_topic",
                bootstrap_servers=config.kafka.kafka_url,
                group_id="auth_service_group",
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                auto_commit_interval_ms=1000,
            ),
            event_consumer=event_consumer,
        )

        auth_consumer_2 = AsyncKafkaConsumer(
            consumer=AIOKafkaConsumer(
                "user_service_topic",
                bootstrap_servers=config.kafka.kafka_url,
                group_id="auth_service_group",
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                auto_commit_interval_ms=1000,
            ),
            event_consumer=event_consumer,
        )

        manager.register_consumer(topic="user_service_topic", consumer=auth_consumer_1)
        manager.register_consumer(topic="user_service_topic", consumer=auth_consumer_2)

        return manager
