from confluent_kafka import Producer,KafkaError,KafkaException
import json

config = {
    "bootstrap.servers" : "kafka:9092"
}


producer = Producer(config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def produce_message(topic,value,key=None):
    try:
        value = json.dumps(value).encode('utf-8')
        producer.produce(
            topic,
            value=value,
            key=key,
            callback=delivery_report
        )
    except KafkaException as e:
        print(f"Error producing message: {e}")

    except KafkaError as e:
        print(f"Kafka error occurred: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
