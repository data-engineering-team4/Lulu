import boto3
import time
from pyspark.sql import SparkSession


if __name__ == "__main__":
    client = boto3.client("kinesis")

    stream_name = "de-4-2-stream"
    consumer_name = "de42"

    shard_iterator = client.get_shard_iterator(
        StreamName=stream_name,
        ShardId="shardId-000000000001",
        ShardIteratorType="LATEST",
    )["ShardIterator"]

    while True:
        response = client.get_records(ShardIterator=shard_iterator, Limit=100)

        for record in response["Records"]:
            data = record["Data"].decode("utf-8")
            print(data)

        shard_iterator = response["NextShardIterator"]

        time.sleep(1)
