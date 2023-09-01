import time
import os
from dotenv import load_dotenv
import json
import boto3

load_dotenv()
kinesis_stream_name = os.environ.get("KINESIS_STREAM_NAME")
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

print(aws_secret_access_key)
client = boto3.client(
    "kinesis",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name="ap-northeast-3",
)
for i in range(100):
    response = client.put_record(
        StreamName=kinesis_stream_name, Data="my_data", PartitionKey="partition_key"
    )
    time.sleep(1)

    print(response)
