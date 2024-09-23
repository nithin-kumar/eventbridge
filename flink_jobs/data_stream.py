from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
import json

def main():
    # Set up the execution environment
    env = StreamExecutionEnvironment.get_execution_environment()

    # Define Kafka consumer properties
    kafka_props = {
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'flink-group'

    }

    # Create a Kafka consumer
    kafka_consumer = FlinkKafkaConsumer(
        topics='events',
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )

    # Add the Kafka consumer as a source to the environment
    stream = env.add_source(kafka_consumer)

    # Print each message
    stream.print()

    # Execute the Flink job
    env.execute('Kafka to Print Job')

if __name__ == '__main__':
    main()