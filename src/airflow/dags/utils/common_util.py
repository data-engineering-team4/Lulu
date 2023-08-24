import pendulum
import datetime


def get_current_datetime():
    local_tz = pendulum.timezone("Asia/Seoul")
    now = pendulum.now(tz=local_tz)
    return now


def get_formatted_date(now):
    ymd = now.strftime('%Y-%m-%d')
    return ymd


def get_formatted_timestamp(now):
    timestamp = now.strftime('%Y-%m-%d_%H:%M:%S')
    return timestamp


def convert_str_to_timestamp(date_str, format='%Y-%m-%d'):
    """
    문자열 형태의 날짜를 timestamp로 변환
    :param date_str: (str) 변환할 날짜 문자열
    :param format: (str, optional) 날짜 문자열의 형식으로, 기본값은 '%Y-%m-%d'
    :return: (int) timestamp
    """
    dt = datetime.datetime.strptime(date_str, format)
    timestamp = int(dt.timestamp())
    return timestamp


def convert_timestamp_to_str(timestamp, format='%Y-%m-%d'):
    """
    timestamp를 문자열 형태의 날짜로 변환
    :param timestamp: (int) 변환할 timestamp
    :param format: (str, optional) 반환될 날짜 문자열의 형식으로, 기본값은 '%Y-%m-%d'
    :return: (str) 날짜 문자열
    """
    dt = datetime.datetime.fromtimestamp(timestamp)
    date_str = dt.strftime(format)
    return date_str


def convert_milliseconds_to_datetime(milliseconds, format='%Y-%m-%d %H:%M'):
    """
    밀리초를 문자열 형태의 날짜와 시간으로 변환
    :param milliseconds: (int) 변환할 밀리초
    :param format: (str, optional) 변환될 날짜와 시간 문자열의 형식으로, 기본값은 '%Y-%m-%d %H:%M'
    :return: (str) 날짜와 시간 문자열
    """
    dt = datetime.datetime.fromtimestamp(milliseconds / 1000)
    date_str = dt.strftime(format)
    return date_str

def upload_to_s3(total_df, type, num):
    import os
    import boto3
    from airflow.models import Variable

    aws_access_key_id = Variable.get('aws_access_key_id')
    aws_secret_access_key = Variable.get('aws_secret_access_key')
    bucket_name = Variable.get('bucket_name')
    s3_folder = Variable.get('s3_folder')
    NOW = get_current_datetime()
    YMD = get_formatted_date(NOW)


    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    temp_csv_path = 'dags/temp_data.csv'
    total_df.to_csv(temp_csv_path, index=False)
    s3.upload_file(temp_csv_path, bucket_name, f'{s3_folder}/{type}/{YMD}/data{num}.csv')
    os.remove(temp_csv_path)

def setup_task(key_num):
    from airflow.providers.redis.hooks.redis import RedisHook
    from airflow.models import Variable
    import logging

    logging.basicConfig(level=logging.INFO)
    api_key = Variable.get(f"RIOT_KEY_{key_num}")

    redis_hook = RedisHook(redis_conn_id='redis_conn_id')
    redis_conn = redis_hook.get_conn()

    return api_key, redis_conn, logging


def generate_fernet_key():
    """
    Fernet key를 발급 받습니다.
    """
    from cryptography.fernet import Fernet

    fernet_key = Fernet.generate_key()
    return fernet_key.decode()


if __name__ == '__main__':
    # export AIRFLOW__CORE__FERNET_KEY=FERNET_KEY
    print(generate_fernet_key())