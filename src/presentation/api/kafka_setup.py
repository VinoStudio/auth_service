import structlog
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from src.settings.config import Config

config: Config = Config()

logger = structlog.getLogger(__name__)


# Create a new topic with multiple partitions
def create_topic_with_partitions():
    admin_client = KafkaAdminClient(
        bootstrap_servers=config.kafka.kafka_url, client_id="auth_service_kafka_admin"
    )

    topic_list = [
        NewTopic(
            name="auth_service_topic",
            num_partitions=6,  # Set desired number of partitions
            replication_factor=1,  # Adjust based on your cluster
        )
    ]

    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        logger.info("Topic created successfully")

    except TopicAlreadyExistsError:
        logger.debug("Topic already exists")
    finally:
        admin_client.close()
