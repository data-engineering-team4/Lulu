import pendulum


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