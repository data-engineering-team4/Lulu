from kinesis.producer import KinesisProducer
import os
from dotenv import load_dotenv
import json
import boto3

load_dotenv()
kinesis_stream_name = os.environ.get("KINESIS_STREAM_NAME")
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

# kinesis_producer = KinesisProducer(
#     stream_name=kinesis_stream_name
# )
# kinesis_producer.put_record(
#     json.dumps("ssssss")
# )
client = boto3.client(
    "kinesis",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name="ap-northeast-3",
)
response = client.put_record(
    StreamName=kinesis_stream_name, Data="my_data", PartitionKey="partition_key"
)
