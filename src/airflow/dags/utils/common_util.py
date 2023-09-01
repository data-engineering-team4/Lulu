import pendulum
import datetime
import json
import io
import logging


def get_current_datetime():
    local_tz = pendulum.timezone("Asia/Seoul")
    now = pendulum.now(tz=local_tz)
    return now


def get_formatted_date(now):
    ymd = now.strftime("%Y-%m-%d")
    return ymd


def get_formatted_timestamp(now):
    timestamp = now.strftime("%Y-%m-%d_%H:%M:%S")
    return timestamp


def convert_str_to_timestamp(date_str, format="%Y-%m-%d"):
    """
    문자열 형태의 날짜를 timestamp로 변환
    :param date_str: (str) 변환할 날짜 문자열
    :param format: (str, optional) 날짜 문자열의 형식으로, 기본값은 '%Y-%m-%d'
    :return: (int) timestamp
    """
    dt = datetime.datetime.strptime(date_str, format)
    timestamp = int(dt.timestamp())
    return timestamp


def convert_timestamp_to_str(timestamp, format="%Y-%m-%d"):
    """
    timestamp를 문자열 형태의 날짜로 변환
    :param timestamp: (int) 변환할 timestamp
    :param format: (str, optional) 반환될 날짜 문자열의 형식으로, 기본값은 '%Y-%m-%d'
    :return: (str) 날짜 문자열
    """
    dt = datetime.datetime.fromtimestamp(timestamp)
    date_str = dt.strftime(format)
    return date_str


def convert_milliseconds_to_datetime(milliseconds, format="%Y-%m-%d %H:%M"):
    """
    밀리초를 문자열 형태의 날짜와 시간으로 변환
    :param milliseconds: (int) 변환할 밀리초
    :param format: (str, optional) 변환될 날짜와 시간 문자열의 형식으로, 기본값은 '%Y-%m-%d %H:%M'
    :return: (str) 날짜와 시간 문자열
    """
    dt = datetime.datetime.fromtimestamp(milliseconds / 1000)
    date_str = dt.strftime(format)
    return date_str


# TODO boto.client3 전역 변수로 빼기
# TODO 2개는 되고 하나는 안되는 이유 -> ECS (성능 문제)
def upload_to_s3(file_path, type, file_name, file_type="parquet"):
    import os
    import boto3
    from airflow.models import Variable

    aws_access_key_id = Variable.get("aws_access_key_id")
    aws_secret_access_key = Variable.get("aws_secret_access_key")
    bucket_name = Variable.get("bucket_name")
    s3_folder = Variable.get("s3_folder")
    NOW = get_current_datetime()
    YMD = get_formatted_date(NOW)

    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    s3.upload_file(
        file_path, bucket_name, f"{s3_folder}/{type}/{YMD}/{file_name}.{file_type}"
    )
    os.remove(file_path)


def download_single_file(s3, bucket_name, key):
    try:
        s3_object = s3.get_object(Bucket=bucket_name, Key=key)
        parquet_data = s3_object["Body"].read()
        return io.BytesIO(parquet_data)
    except Exception as e:
        logging.error(f"Failed to download {key} due to {e}")
        return None


def download_from_s3(type="match", file_type=".parquet"):
    from airflow.models import Variable
    import boto3
    from concurrent.futures import ThreadPoolExecutor
    from .constants import RAW_MASTERY_BUCKET, RAW_MATCH_BUCKET

    aws_access_key_id = Variable.get("aws_access_key_id")
    aws_secret_access_key = Variable.get("aws_secret_access_key")
    bucket_name = Variable.get("bucket_name")
    s3_folder = Variable.get("s3_folder")
    NOW = get_current_datetime()
    YMD = get_formatted_date(NOW)

    sub_folder = RAW_MATCH_BUCKET
    if type == "mastery":
        sub_folder = RAW_MASTERY_BUCKET

    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    s3_objects = s3.list_objects(
        Bucket=bucket_name, Prefix=f"{s3_folder}/{sub_folder}/{YMD}"
    )

    if "Contents" in s3_objects:
        keys = [
            obj["Key"]
            for obj in s3_objects["Contents"]
            if obj["Key"].endswith(file_type)
        ]

        with ThreadPoolExecutor() as executor:
            parquet_files = list(
                executor.map(
                    lambda key: download_single_file(s3, bucket_name, key), keys
                )
            )

        parquet_files = [f for f in parquet_files if f is not None]

        if not parquet_files:
            logging.info("All files failed to download.")
            return []

        logging.info(f"Successfully downloaded {len(parquet_files)} files.")
        return parquet_files
    else:
        logging.info(
            f"No files found in the specified S3 location. ({s3_folder}/{sub_folder}/{YMD})"
        )
        return []


def setup_task(key_num):
    from airflow.providers.redis.hooks.redis import RedisHook
    from airflow.models import Variable
    import logging

    logging.basicConfig(level=logging.INFO)
    api_key = Variable.get(f"RIOT_KEY_{key_num}")

    redis_hook = RedisHook(redis_conn_id="redis_conn_id")
    redis_conn = redis_hook.get_conn()

    return api_key, redis_conn, logging


def verify_data_in_redis(redis_conn, key):
    data_bytes = redis_conn.get(key)
    if data_bytes:
        logging.info(f"Data exists for key: {key}")
        logging.info(f"Data: {data_bytes.decode('utf-8')}")
    else:
        logging.warning(f"No data found for key: {key}")


def load_from_redis(redis_conn, key):
    data_bytes = redis_conn.get(key)
    if data_bytes:
        data_json = data_bytes.decode("utf-8")
        return json.loads(data_json)
    else:
        return []


def generate_fernet_key():
    """
    Fernet key를 발급 받습니다.
    """
    from cryptography.fernet import Fernet

    fernet_key = Fernet.generate_key()
    return fernet_key.decode()
