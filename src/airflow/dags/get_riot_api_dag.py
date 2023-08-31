# Airflow 관련 모듈 임포트
from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

# 유틸리티 및 상수 모듈 임포트
from utils.slack_alert import SlackAlert
from utils.request_limiter import RequestLimiter
from utils.constants import (
    TIERS,
    DIVISIONS,
    HIGH_ELO_LIST,
    TIER_MATCH_COUNT,
    S3_UPLOAD_THRESHOLD,
    MATCH_THRESHOLD,
    RAW_MATCH_BUCKET,
    RAW_MASTERY_BUCKET,
)

# Riot API 관련 유틸리티 모듈 임포트
from utils.riot_util import (
    get_summoner_info_by_tier_division_page,
    get_high_elo_summoner_info,
)

# 파일 저장 및 로깅 관련 모듈 임포트
from utils.common_util import upload_to_s3
import pyarrow as pa
import pyarrow.parquet as pq
import logging

# JSON 관련 모듈 임포트
import json

# 시간 관련 모듈 임포트
import time

SEVEN_DAYS_AGO = datetime.now() - timedelta(days=14)
SEVEN_DAYS_AGO_TIMESTAMP = int(SEVEN_DAYS_AGO.timestamp())

# API 요청 제한 설정
limiters = {
    # (1초당 최대 요청 수 20개, 2분당 최대 요청 수 100개)
    1: (
        RequestLimiter(max_requests=20, per_seconds=1),
        RequestLimiter(max_requests=100, per_seconds=120),
    ),
    2: (
        RequestLimiter(max_requests=20, per_seconds=1),
        RequestLimiter(max_requests=100, per_seconds=120),
    ),
    3: (
        RequestLimiter(max_requests=20, per_seconds=1),
        RequestLimiter(max_requests=100, per_seconds=120),
    ),
    4: (
        RequestLimiter(max_requests=20, per_seconds=1),
        RequestLimiter(max_requests=100, per_seconds=120),
    ),
}


def _wait_for_request(key):
    one_second_limiter, two_minute_limiter = limiters[key]

    while True:
        one_second_limiter.wait_for_request_slot()
        two_minute_limiter.wait_for_request_slot()

        if (
            one_second_limiter.requests < one_second_limiter.max_requests
            and two_minute_limiter.requests < two_minute_limiter.max_requests
        ):
            break


def _process_summoner_data(
    tier, division, page, api_key, redis_conn, processed_ids, key_num, logging
):
    try:
        json_data = get_summoner_info_by_tier_division_page(
            tier, division, page, api_key
        )
        _wait_for_request(key_num)  # API 요청 제한 확인

        for data in json_data:
            summoner_id = data["summonerId"]
            if summoner_id not in processed_ids:
                summoner_data = {
                    "tier": tier,
                    "division": division,
                    "summoner_id": summoner_id,
                    "summoner_name": data["summonerName"],
                }
                redis_conn.sadd(f"summoner_data_{key_num}", json.dumps(summoner_data))
                redis_conn.sadd("processed_summoners_ids", summoner_id)
    except KeyError:
        logging.error("API 키 제한")
        time.sleep(1.2)


def _process_high_elo_data(
    high_elo, api_key, redis_conn, processed_ids, key_num, logging
):
    try:
        json_data = get_high_elo_summoner_info(high_elo.lower(), api_key)
        _wait_for_request(key_num)
        json_data_length = len(json_data["entries"])

        # 월요일:0, 화요일: 1, ... 일요일: 6
        current_day_of_week = datetime.today().weekday()
        today_start_index = (current_day_of_week * json_data_length) // 7

        if current_day_of_week != 6:
            today_end_index = ((current_day_of_week + 1) * json_data_length) // 7
        else:
            today_end_index = json_data_length

        segment_length = (today_end_index - today_start_index) // 3

        key_num_start_index = today_start_index + segment_length * key_num
        key_num_end_index = (
            (key_num_start_index + segment_length) if key_num != 2 else today_end_index
        )

        selected_entries = json_data["entries"][key_num_start_index:key_num_end_index]

        for data in selected_entries:
            summoner_id = data["summonerId"]
            if summoner_id not in processed_ids:
                high_elo_summoner_data = {
                    "tier": high_elo,
                    "division": "0",
                    "summoner_id": summoner_id,
                    "summoner_name": data["summonerName"],
                }
                redis_conn.sadd(
                    f"summoner_data_{key_num}", json.dumps(high_elo_summoner_data)
                )
                redis_conn.sadd("processed_summoners_ids", summoner_id)
    except KeyError:
        logging.error("API 키 제한")
        time.sleep(1.2)


def _categorize_tier_data(summoner_ids):
    from collections import defaultdict

    tier_data = defaultdict(list)
    for summoner in summoner_ids:
        tier = summoner.get("tier")
        if tier and tier not in HIGH_ELO_LIST:
            tier += summoner.get("division")
        tier_data[tier].append(summoner)
    return tier_data


def _process_matches(
    matches, processed_match_ids, existing_matches, redis_conn, match_list
):
    unique_matches = [match for match in matches if match not in processed_match_ids]

    if unique_matches:
        if len(match_list) + len(matches) > TIER_MATCH_COUNT:
            needed_matches = TIER_MATCH_COUNT - len(match_list)
            match_list.extend(matches[:needed_matches])
            match_ids_to_add = [match for match in unique_matches[:needed_matches]]
            processed_match_ids.update(match_ids_to_add)
            redis_conn.sadd(existing_matches, *match_ids_to_add)
        else:
            match_list.extend(matches)
            processed_match_ids.update(unique_matches)
            redis_conn.sadd(existing_matches, *unique_matches)


def _save_to_s3(rows, unique_parquet_name, schema_fields, column_names, s3_folder):
    # 동적 스키마 생성
    schema = pa.schema(schema_fields)

    # 동적 테이블 생성
    table_data = {col: [x[i] for x in rows] for i, col in enumerate(column_names)}
    table = pa.table(table_data, schema=schema)

    # 임시 파일 경로
    temp_parquet_path = f"dags/temp_data_{unique_parquet_name}"

    # Parquet 파일 작성
    pq.write_table(table, temp_parquet_path)

    # S3 업로드
    upload_to_s3(temp_parquet_path, s3_folder, unique_parquet_name)

    logging.info(
        f"🚀Successfully uploaded {unique_parquet_name} to S3 in folder {s3_folder}."
    )


with DAG(
    dag_id="get_riot_api",
    schedule_interval=None,
    # schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 8, 17),
    catchup=False,
) as dag:

    @task()
    def get_summoners_by_tier(key_num):
        from utils.common_util import setup_task

        api_key, redis_conn, logging = setup_task(key_num)
        processed_summoner_ids = set(
            member.decode() for member in redis_conn.smembers("processed_summoners_ids")
        )
        logging.info(f"🚀processed_summoner_ids : {len(processed_summoner_ids)}")

        days_since_start = (
            datetime.now() - datetime(2023, 8, 17)
        ).days  # 작업이 처음 시작된 날짜로부터 지금까지 몇 일이 지났는지 계산
        start_page = (
            days_since_start * 4
        ) % 200  # 지난 날 수에 4를 곱하고 200으로 나눈 나머지를 시작 페이지로 설정
        page = start_page + key_num  # 시작 페이지에 key_num을 더해 각 작업에 대한 고유한 페이지 번호 생성

        # 각 티어와 디비전 별로 소환사 정보 수집
        for tier in TIERS:
            for division in DIVISIONS:
                _process_summoner_data(
                    tier,
                    division,
                    page,
                    api_key,
                    redis_conn,
                    processed_summoner_ids,
                    key_num,
                    logging,
                )

        # 고위 레벨 소환사 데이터 처리
        for high_elo in HIGH_ELO_LIST:
            _process_high_elo_data(
                high_elo, api_key, redis_conn, processed_summoner_ids, key_num, logging
            )

        logging.info(f"😎get_summoners_by_tier finished")

    @task()
    def get_match_list(key_num):
        from utils.common_util import setup_task
        from utils.riot_util import get_puuid_by_id, get_match_history
        import json

        api_key, redis_conn, logging = setup_task(key_num)

        existing_match = "processed_match_ids"
        processed_match_ids = set(
            member.decode() for member in redis_conn.smembers(existing_match)
        )
        summoner_part = f"summoner_data_{key_num}"
        summoner_ids = [
            json.loads(member.decode()) for member in redis_conn.smembers(summoner_part)
        ]
        tier_data = _categorize_tier_data(summoner_ids)

        logging.info(f"🚀 categorize_tier_data : {len(tier_data)}")

        match_list_by_tier = {tier: [] for tier in HIGH_ELO_LIST}
        match_list_by_tier.update(
            {f"{tier}{division}": [] for tier in TIERS for division in DIVISIONS}
        )

        is_finished = False
        for tier, summoners in tier_data.items():
            if is_finished:
                break

            logging.info(f"🚀Processing tier: {tier}")
            for summoner in summoners:
                # tier별로 조건을 검사
                if len(match_list_by_tier[tier]) >= TIER_MATCH_COUNT:
                    logging.info(f"🚀{tier}는 이미 충분한 데이터를 수집했습니다. 다음 tier로 넘어갑니다.")
                    break

                try:
                    _wait_for_request(key_num)

                    puuid = get_puuid_by_id(summoner.get("summoner_id"), api_key)
                    summoner["puuid"] = puuid if puuid else None

                    if not puuid:
                        logging.error(
                            f"🚨 Failed to fetch puuid for {summoner['summoner_name']}"
                        )

                    matches = get_match_history(
                        puuid, SEVEN_DAYS_AGO_TIMESTAMP, 1, MATCH_THRESHOLD, api_key
                    )
                    _process_matches(
                        matches,
                        processed_match_ids,
                        existing_match,
                        redis_conn,
                        match_list_by_tier[tier],
                    )

                    if all(
                        len(match_list) >= TIER_MATCH_COUNT
                        for match_list in match_list_by_tier.values()
                    ):
                        is_finished = True
                        break
                except KeyError as e:
                    logging.warning(
                        f"🚨KeyError가 발생했습니다 ({e}): {summoner['summoner_name']}을(를) 처리하는 중"
                    )
                    time.sleep(5)
                except Exception as e:
                    logging.info(f"🚨예외가 발생했습니다: {e}")

        if is_finished:
            logging.info("😎get_match_list finished")

    @task()
    def extract_match_data(key_num):
        from utils.riot_util import get_match_details
        from utils.common_util import setup_task, save_to_redis, load_from_redis
        import pyarrow as pa
        import json

        api_key, redis_conn, logging = setup_task(key_num)

        schema_fields = pa.schema(
            [
                ("tier", pa.string()),
                ("match_id", pa.string()),
                ("match_details", pa.string()),
            ]
        )

        column_names = ["tier", "match_id", "match_details"]

        if not redis_conn.ping():
            logging.error("🚨Redis 서버에 연결할 수 없습니다.")
            return

        try:
            redis_key = f"match_data_{key_num}"
            match_data_set = [
                member.decode() for member in redis_conn.smembers(redis_key)
            ]

            all_data_key = f"all_data_{key_num}"
            all_data = load_from_redis(redis_conn, all_data_key)
            logging.info(f"🚀Loaded all_data with length: {len(all_data)}")
            logging.info(f"🚀Type of all_data: {type(all_data)}")

            match_detail_rows = []
            batch_count = 0
            for index, match_data in enumerate(match_data_set):
                try:
                    match = json.loads(match_data)
                except json.JSONDecodeError as e:
                    logging.error(f"🚨JSON decoding error: {e}")
                    continue

                tier = match.get("tier", "Unknown")  # KeyError 방지
                match_id = match.get("matchId", "Unknown")  # KeyError 방지

                try:
                    if index % 50 == 0:
                        logging.info(f"🚀Extract match {index}번째 실행중...")
                    match_details = get_match_details(match_id, api_key)
                    _wait_for_request(key_num)
                except Exception as e:
                    logging.error(f"🚨Failed to get match details: {e}")
                    continue

                row = (tier, match_id, json.dumps(match_details))
                match_detail_rows.append(row)
                all_data.append(row)

                # 1000개의 row가 쌓이면 S3에 업로드
                if len(match_detail_rows) >= S3_UPLOAD_THRESHOLD:
                    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
                    batch_count += 1
                    unique_parquet_name = (
                        f"data_{key_num}_{current_time}_batch{batch_count}"
                    )

                    logging.info(
                        f"🚀Uploading a batch with {S3_UPLOAD_THRESHOLD} rows as {unique_parquet_name}..."
                    )
                    _save_to_s3(
                        match_detail_rows,
                        unique_parquet_name,
                        schema_fields,
                        column_names,
                        RAW_MATCH_BUCKET,
                    )
                    match_detail_rows.clear()  # 메모리를 비움

            # for문이 끝난 후 남은 데이터 업로드
            if len(match_detail_rows) > 0:
                current_time = datetime.now().strftime("%Y%m%d%H%M%S")
                batch_count += 1
                unique_parquet_name = (
                    f"data_{key_num}_{current_time}_batch{batch_count}_last"
                )

                logging.info(
                    f"🚀Uploading the last batch with {len(match_detail_rows)} rows as {unique_parquet_name}..."
                )
                _save_to_s3(
                    match_detail_rows,
                    unique_parquet_name,
                    schema_fields,
                    column_names,
                    RAW_MATCH_BUCKET,
                )

            save_to_redis(redis_conn, all_data_key, all_data)

        except Exception as e:
            logging.error(f"🚨An unexpected error occurred: {e}")

    @task
    def get_champion_mastery(key_num):
        from utils.common_util import setup_task
        from utils.riot_util import get_champion_mastery_by_id
        import pyarrow as pa
        import json

        api_key, redis_conn, logging = setup_task(key_num)

        schema_fields = pa.schema(
            [("summoner_id", pa.string()), ("mastery_details", pa.string())]
        )

        column_names = ["summoner_id", "mastery_details"]

        if not redis_conn.ping():
            logging.error("🚨Redis 서버에 연결할 수 없습니다.")
            return

        redis_key = f"summoner_data_{key_num}"
        summoner_ids = [
            json.loads(member.decode()) for member in redis_conn.smembers(redis_key)
        ]

        id_list = [summoner["summoner_id"] for summoner in summoner_ids]

        mastery_data_rows = []
        batch_count = 0

        for index, id in enumerate(id_list):
            try:
                if index % 50 == 0:
                    logging.info(f"🚀Extract mastery {index}번째 실행중...")
                mastery_data = get_champion_mastery_by_id(id, api_key)
                _wait_for_request(key_num)
            except Exception as e:
                logging.error(f"🚨Failed to get mastery details: {e}")
                continue

            row = (id, json.dumps(mastery_data))
            mastery_data_rows.append(row)

            # 1000개의 row가 쌓이면 S3에 업로드
            if len(mastery_data_rows) >= S3_UPLOAD_THRESHOLD:
                current_time = datetime.now().strftime("%Y%m%d%H%M%S")
                batch_count += 1
                unique_parquet_name = (
                    f"data_{key_num}_{current_time}_batch{batch_count}"
                )

                logging.info(
                    f"🚀Uploading a batch with {S3_UPLOAD_THRESHOLD} rows as {unique_parquet_name}..."
                )
                _save_to_s3(
                    mastery_data_rows,
                    unique_parquet_name,
                    schema_fields,
                    column_names,
                    RAW_MASTERY_BUCKET,
                )
                mastery_data_rows.clear()  # 메모리를 비움

        # for문이 끝난 후 남은 데이터 업로드
        if len(mastery_data_rows) > 0:
            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
            batch_count += 1
            unique_parquet_name = (
                f"data_{key_num}_{current_time}_batch{batch_count}_last"
            )

            logging.info(
                f"🚀Uploading the last batch with {len(mastery_data_rows)} rows as {unique_parquet_name}..."
            )
            _save_to_s3(
                mastery_data_rows,
                unique_parquet_name,
                schema_fields,
                column_names,
                RAW_MASTERY_BUCKET,
            )

    @task()
    def delete_redis_key():
        from utils.common_util import setup_task

        api_key, redis_conn, logging = setup_task(1)
        for key in range(1, 4):
            summoner_data_key = f"summoner_data_{key}"
            match_data_key = f"match_data_{key}"

            redis_conn.delete(summoner_data_key)
            redis_conn.delete(match_data_key)

    start = EmptyOperator(task_id="start")

    with TaskGroup(group_id="summoners_task_group") as summoners_task_group:
        summoners_task_1 = get_summoners_by_tier(1)
        summoners_task_2 = get_summoners_by_tier(2)
        summoners_task_3 = get_summoners_by_tier(3)


    with TaskGroup(group_id="match_list_task_group") as match_list_task_group:
        match_list_task_1 = get_match_list(1)
        match_list_task_2 = get_match_list(2)
        match_list_task_3 = get_match_list(3)


    with TaskGroup(group_id="match_extract_group") as match_extract_group:
        match_extract_task_1 = extract_match_data(1)
        match_extract_task_2 = extract_match_data(2)
        match_extract_task_3 = extract_match_data(3)


    with TaskGroup(group_id="mastery_extract_group") as mastery_extract_group:
        mastery_extract_task_1 = get_champion_mastery(1)
        mastery_extract_task_2 = get_champion_mastery(2)
        mastery_extract_task_3 = get_champion_mastery(3)

    delete_redis_key_task = delete_redis_key()

    slack_alert = SlackAlert(channel="#lulu-airflow-alert")
    match_extract_end = EmptyOperator(
        task_id="match_extract_end",
        on_success_callback=slack_alert.slack_success_alert,
        on_failure_callback=slack_alert.slack_failure_alert,
    )

    mastery_extract_end = EmptyOperator(
        task_id="mastery_extract_end",
        on_success_callback=slack_alert.slack_success_alert,
        on_failure_callback=slack_alert.slack_failure_alert,
    )

    end = EmptyOperator(task_id="end")

    start >> summoners_task_group >> match_list_task_group >> match_extract_group
    (
        match_extract_group
        >> match_extract_end
        >> mastery_extract_group
        >> mastery_extract_end
        >> delete_redis_key_task
        >> end
    )
