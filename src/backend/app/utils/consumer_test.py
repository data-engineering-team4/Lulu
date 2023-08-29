from kinesis.consumer import KinesisConsumer
import os
from dotenv import load_dotenv

load_dotenv()

kinesis_stream_name = os.environ.get("KINESIS_STREAM_NAME")
consumer = KinesisConsumer(stream_name=kinesis_stream_name)

for message in consumer:
    print(message)