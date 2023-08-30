import pendulum
import datetime
import json


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


def upload_to_s3(file_path, type, file_name, file_type='parquet'):
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



def setup_task(key_num):
    from airflow.providers.redis.hooks.redis import RedisHook
    from airflow.models import Variable
    import logging

    logging.basicConfig(level=logging.INFO)
    api_key = Variable.get(f"RIOT_KEY_{key_num}")

    redis_hook = RedisHook(redis_conn_id="redis_conn_id")
    redis_conn = redis_hook.get_conn()

    return api_key, redis_conn, logging


def save_to_redis(redis_conn, key, data):
    redis_conn.set(key, data)


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
