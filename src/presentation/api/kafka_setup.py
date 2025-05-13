import structlog
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from src.settings.config import Config

config: Config = Config()

logger = structlog.getLogger(__name__)


def create_kafka_topic(
    topic_name: str = "auth_service_topic",
    num_partitions: int = 6,
    replication_factor: int = 1,
    bootstrap_servers: str | None = None,
    client_id: str | None = None,
    topic_configs: dict[str] | None = None,
) -> None:
    """
    Create a Kafka topic with specified partitions and configuration.

    Args:
        topic_name (str): Name of the topic to create
        num_partitions (int): Number of partitions for the topic
        replication_factor (int): Replication factor for the topic
        bootstrap_servers (str): Kafka bootstrap servers URL
        client_id (str): Client ID for the Kafka admin client
        topic_configs (dict[str]): Additional topic configuration options

    Returns:
        None
    """
    # Use configuration defaults if not specified
    servers = bootstrap_servers or config.kafka.kafka_url
    kafka_client_id = client_id or "auth_service_kafka_admin"

    admin_client = None
    try:
        # Create admin client
        admin_client = KafkaAdminClient(
            bootstrap_servers=servers, client_id=kafka_client_id
        )

        # Create topic
        new_topic = NewTopic(
            name=topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
            topic_configs=topic_configs,
        )

        admin_client.create_topics(new_topics=[new_topic], validate_only=False)
        logger.info(
            "Topic '{topic_name}' created successfully with {num_partitions} partitions",
            topic_name=topic_name,
            num_partitions=num_partitions,
        )

    except TopicAlreadyExistsError:
        logger.info("Topic '{topic_name}' already exists", topic_name=topic_name)

    finally:
        if admin_client:
            admin_client.close()
