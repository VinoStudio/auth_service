from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from settings.config import Config

config: Config = Config()


# Create a new topic with multiple partitions
async def create_topic_with_partitions():
    admin_client = KafkaAdminClient(
        bootstrap_servers=config.kafka.kafka_url, client_id="user_service_kafka_admin"
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
        print(f"Created topic with {topic_list[0].num_partitions} partitions")
    except TopicAlreadyExistsError:
        print("Topic already exists")
    finally:
        admin_client.close()
