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


# def create_kafka_topic(
#         topic_name="auth_service_topic",
#         num_partitions=6,
#         replication_factor=1,
#         bootstrap_servers=None,
#         client_id=None,
#         topic_configs=None
# ):
#     """
#     Create a Kafka topic with specified partitions and configuration.
#
#     Args:
#         topic_name (str): Name of the topic to create
#         num_partitions (int): Number of partitions for the topic
#         replication_factor (int): Replication factor for the topic
#         bootstrap_servers (str): Kafka bootstrap servers URL
#         client_id (str): Client ID for the Kafka admin client
#         topic_configs (dict): Additional topic configuration options
#
#     Returns:
#         bool: True if topic was created or already exists, False if creation failed
#     """
#     # Use configuration defaults if not specified
#     servers = bootstrap_servers or config.kafka.kafka_url
#     kafka_client_id = client_id or "auth_service_kafka_admin"
#
#     admin_client = None
#     try:
#         # Create admin client
#         admin_client = KafkaAdminClient(
#             bootstrap_servers=servers,
#             client_id=kafka_client_id
#         )
#
#         # Create topic
#         new_topic = NewTopic(
#             name=topic_name,
#             num_partitions=num_partitions,
#             replication_factor=replication_factor,
#             topic_configs=topic_configs or {}
#         )
#
#         admin_client.create_topics(new_topics=[new_topic], validate_only=False)
#         logger.info(f"Topic '{topic_name}' created successfully with {num_partitions} partitions")
#         return True
#
#     except TopicAlreadyExistsError:
#         logger.info(f"Topic '{topic_name}' already exists")
#         return True  # Consider this a success case
#     except Exception as e:
#         logger.error(f"Failed to create topic '{topic_name}': {str(e)}")
#         return False
#     finally:
#         if admin_client:
#             admin_client.close()
