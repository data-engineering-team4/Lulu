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