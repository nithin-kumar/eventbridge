import json
import logging
import os

from pyflink.common import WatermarkStrategy, Encoder
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FileSink, RollingPolicy, OutputFileConfig
from pyflink.datastream.connectors.kafka import KafkaOffsetsInitializer, KafkaSource
import boto3

from dynamodb_client import DynamoDBClientSingleton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def process_event(event):
    """Process each event and print the parsed data"""
    event_data = json.loads(event)
    dynamo_client = DynamoDBClientSingleton()
    table = dynamo_client.get_table('events')
    table.put_item(Item=event_data)
    return event


def write_to_dynamo_db():
    """A Flink task which sinks a kafka topic to dynamo db"""
    # Create a StreamExecutionEnvironment
    env = StreamExecutionEnvironment.get_execution_environment()

    # the kafka/sql jar is used here as it's a fat jar and could avoid dependency issues
    env.add_jars("file:///jars/flink-sql-connector-kafka-3.0.1-1.18.jar")

    # Define the new kafka source with our docker brokers/topics
    # This creates a source which will listen to our kafka broker
    # on the topic we created. It will read from the earliest offset
    # and just use a simple string schema for serialization (no JSON/Proto/etc)
    kafka_source = (
        KafkaSource.builder()
        .set_bootstrap_servers(os.environ["KAFKA_BROKER"])
        .set_topics(os.environ["KAFKA_TOPIC"])
        .set_group_id("flink_group")
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    # Adding our kafka source to our environment
    stream = env.from_source(kafka_source, WatermarkStrategy.no_watermarks(), "Kafka Source")
    stream.map(process_event)

    # Execute the job and submit the job
    print("Processed Kafka events")
    env.execute("write_to_dynamo_db")


if __name__ == "__main__":
    write_to_dynamo_db()