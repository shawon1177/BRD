from confluent_kafka import Producer
import json
import logging

logger = logging.getLogger(__name__)

config = {
    "bootstrap.servers": "kafka:9092",
    "client.id": "django-producer",
}

producer = Producer(config)


def delivery_report(err, msg):
    if err:
        logger.error("Kafka delivery failed: %s", err)
    else:
        logger.info(
            "Delivered to %s [%s] offset %s",
            msg.topic(),
            msg.partition(),
            msg.offset(),
        )


def produce_message(topic, value, key=None):
    try:
        producer.produce(
            topic=topic,
            value=json.dumps(value).encode("utf-8"),
            key=key,
            callback=delivery_report,
        )

        # Serve delivery callbacks without blocking.
        producer.poll(0)

    except Exception:
        logger.exception("Failed to produce Kafka message")


def tracklocation(topic, value, key=None):
    try:
        producer.produce(
            topic=topic,
            value=json.dumps(value).encode("utf-8"),
            key=key,
            callback=delivery_report,
        )

        producer.poll(0)

    except Exception:
        logger.exception("Failed to produce location message")