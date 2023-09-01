from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta
import logging
import pandas as pd
import json
from tempfile import NamedTemporaryFile
import os

from utils.slack_alert import SlackAlert
from utils.constants import TRANSFORMED_MATCH_BUCKET, TRANSFORMED_MASTERY_BUCKET


def _merge_parquet_files(parquet_files):
    merged_dataframe = pd.DataFrame()
    for idx, parquet_file in enumerate(parquet_files):
        try:
            dataframe = pd.read_parquet(parquet_file)
            logging.info(
                f"🚀Successfully read {parquet_file}. DataFrame shape: {dataframe.shape}"
            )
            logging.info(f"DataFrame columns: {dataframe.columns}")
            merged_dataframe = pd.concat([merged_dataframe, dataframe])
        except Exception as e:
            logging.error(
                f"🚨Failed to read or merge a dataframe at index {idx} due to {e}"
            )
    return merged_dataframe


def _extract_match_details(row):
    import os

    def _extract_values(participants, key):
        return [participant[key] for participant in participants]

    def _extract_bans(teams):
        bans_list = []
        for team in teams:
            if "bans" in team:
                bans = [ban_info["championId"] for ban_info in team["bans"]]
            else:
                bans = [-1] * 5  # ban 정보가 없는 경우 -1로 채웁니다.
            bans_list.extend(bans)
        return bans_list

    if isinstance(row["match_details"], str):  # match_details가 문자열 형태인 경우
        details = json.loads(row["match_details"])
    elif isinstance(row["match_details"], dict):  # 이미 딕셔너리 형태인 경우
        details = row["match_details"]
    else:
        print("Unknown data type for match_details")
        return

    if "info" in details:
        participants = details["info"]["participants"]
        bans = _extract_bans(details["info"]["teams"])

        # load champion mapping data
        script_path = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(script_path, "utils", "champion_dictionary.json")
        with open(json_file_path, "r") as f:
            champion_dict = json.load(f)

        patch = ".".join(str(details["info"]["gameVersion"]).split(".")[0:2])
        banned_champion_names = [
            champion_dict.get(str(ban_id), "Unknown") for ban_id in bans
        ]

        return pd.Series(
            {
                "team_id": _extract_values(participants, "teamId"),
                "position": _extract_values(participants, "teamPosition"),
                "kills": _extract_values(participants, "kills"),
                "deaths": _extract_values(participants, "deaths"),
                "assists": _extract_values(participants, "assists"),
                "win": _extract_values(participants, "win"),
                "champion_name": _extract_values(participants, "championName"),
                "champion_id": _extract_values(participants, "championId"),
                "banned_champion_id": bans,  # 밴 정보 추가
                "banned_champion_name": banned_champion_names,  # 밴된 챔피언 이름 추가
                "patch": patch,
                "tier": row["tier"],
                "match_id": row["match_id"],
            }
        )
    elif "status" in details:
        print(f"Skipping row due to status: {details['status']}")
        return pd.Series()
    else:
        print(f"Skipping row due to missing 'info' and 'status' keys: {row}")
        return pd.Series()


def _expand_row(row):
    # 리스트로 되어 있는 컬럼들
    list_columns = [
        "team_id",
        "position",
        "kills",
        "deaths",
        "assists",
        "win",
        "champion_name",
        "champion_id",
        "banned_champion_name",
        "banned_champion_id",
    ]

    # Scalar 값으로 되어 있는 컬럼들
    scalar_columns = ["patch", "tier", "match_id"]

    # 새로운 row들을 저장할 리스트
    new_rows = []

    # 리스트 길이 확인 (모든 리스트 컬럼은 길이가 동일하다고 가정)
    lengths = [len(row[col]) for col in list_columns]

    # 길이가 모두 동일한지 확인
    if len(set(lengths)) != 1:
        print(f"Skipping row due to inconsistent list lengths: {lengths}")
        return pd.DataFrame()  # 빈 DataFrame 반환

    n = lengths[0]  # 리스트의 길이

    for i in range(n):
        new_row = {}
        for col in list_columns:
            new_row[col] = row[col][i]

        for col in scalar_columns:
            new_row[col] = row[col]

        new_rows.append(new_row)

    return pd.DataFrame(new_rows)


def _load_mastery_details(row, champion_dict):
    tmp_str = row["mastery_details"]
    try:
        tmp = json.loads(tmp_str) if tmp_str is not None else []
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding failed for summoner_id {row['summoner_id']}: {e}")
        return None

    data = {"id": row["summoner_id"]}

    for key in champion_dict.keys():
        if key != "id":
            data[key] = 0

    for champion in tmp:
        if "championId" in champion and "championPoints" in champion:
            champion_id = champion["championId"]
            champion_points = champion["championPoints"]
            if str(champion_id) in data:
                data[str(champion_id)] = champion_points

    return data


def _create_total_dataframe(mastery_df, champion_dict):
    data_list = []
    for _, row in mastery_df.iterrows():
        data = _load_mastery_details(row, champion_dict)
        if data is not None:
            data_list.append(data)

    if not data_list:
        logging.error("No data processed. DataFrame will be empty.")
        return pd.DataFrame()

    total_df = pd.DataFrame(data_list)
    logging.info("😎Successfully created the total DataFrame.")
    return total_df


with DAG(
    dag_id="transform_riot_data",
    schedule_interval=None,
    # schedule_interval=timedelta(days=14),
    start_date=datetime(2023, 8, 29),
    catchup=False,
) as dag:

    @task()
    def transform_match_data():
        from utils.common_util import download_from_s3, upload_to_s3

        # S3에서 파일 다운로드
        logging.info("📥 Downloading parquet files from S3...")
        parquet_files = download_from_s3("match")

        if parquet_files:
            logging.info(f"🔍 Found {len(parquet_files)} parquet files.")

            # 파일 병합
            logging.info("🔄 Merging parquet files...")
            merged_dataframe = _merge_parquet_files(parquet_files)

            # 데이터 변환
            logging.info("🔄 Transforming data...")
            transformed_dataframe = merged_dataframe.apply(
                _extract_match_details, axis=1
            )
            logging.info(
                f"✔️ Transformed dataframe shape: {transformed_dataframe.shape}"
            )

            # DataFrame 확장
            logging.info("🔄 Expanding DataFrame rows...")
            expanded_df_list = []
            for idx, row in transformed_dataframe.iterrows():
                try:
                    expanded_df = _expand_row(row)
                    expanded_df_list.append(expanded_df)
                except ValueError as ve:
                    logging.error(f"🚨 ValueError at row {idx}: {ve}")
                except Exception as e:
                    logging.error(f"🚨 Unexpected error at row {idx}: {e}")

            if not expanded_df_list:
                logging.error("🚨 No data to process after expanding rows.")
                return

            final_expanded_df = pd.concat(expanded_df_list, ignore_index=True)

            # S3에 업로드하기 전에 데이터 분할
            logging.info("🔄 Chunking data...")
            chunk_size = 50000  # 적절한 크기로 설정
            total_chunks = len(final_expanded_df) // chunk_size + 1

            for i in range(total_chunks):
                logging.info(f"📤 Uploading chunk {i + 1}/{total_chunks} to S3...")
                chunk_df = final_expanded_df.iloc[i * chunk_size : (i + 1) * chunk_size]

                try:
                    with NamedTemporaryFile(
                        suffix=".csv", delete=False
                    ) as temp_file:  # delete=False로 설정
                        chunk_df.to_csv(temp_file.name, index=True)
                        # S3에 업로드
                        upload_to_s3(
                            temp_file.name,
                            TRANSFORMED_MATCH_BUCKET,
                            f"transformed_match_data_chunk_{i}",
                            file_type="csv",
                        )
                except Exception as e:
                    logging.error(f"🚨 Error during file operation: {e}")
                finally:
                    if os.path.exists(temp_file.name):  # 파일이 존재하는지 확인
                        os.unlink(temp_file.name)  # 임시 파일 삭제

            logging.info("✔️ Data upload complete.")

    @task()
    def transform_mastery_data():
        from utils.common_util import download_from_s3, upload_to_s3

        # S3에서 파일 다운로드
        logging.info("📥 Downloading parquet files from S3...")
        parquet_files = download_from_s3("mastery")

        # load champion mapping data
        script_path = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(script_path, "utils", "champion_dictionary.json")
        with open(json_file_path, "r") as f:
            champion_dict = json.load(f)

        if parquet_files:
            logging.info(f"🔍 Found {len(parquet_files)} parquet files.")

            # 파일 병합
            logging.info("🔄 Merging parquet files...")
            merged_dataframe = _merge_parquet_files(parquet_files)

            # 데이터 변환
            logging.info("🔄 Transforming data...")
            transformed_dataframe = _create_total_dataframe(
                merged_dataframe, champion_dict
            )
            logging.info(
                f"✔️ Transformed dataframe shape: {transformed_dataframe.shape}"
            )

            # S3에 업로드하기 전에 데이터 분할
            logging.info("🔄 Chunking data...")
            chunk_size = 50000  # 적절한 크기로 설정
            total_chunks = len(transformed_dataframe) // chunk_size + 1

            for i in range(total_chunks):
                logging.info(f"📤 Uploading chunk {i + 1}/{total_chunks} to S3...")
                chunk_df = transformed_dataframe.iloc[
                    i * chunk_size : (i + 1) * chunk_size
                ]

                try:
                    with NamedTemporaryFile(
                        suffix=".csv", delete=False
                    ) as temp_file:  # delete=False로 설정
                        chunk_df.to_csv(temp_file.name, index=True)
                        # S3에 업로드
                        upload_to_s3(
                            temp_file.name,
                            TRANSFORMED_MASTERY_BUCKET,
                            f"transformed_mastery_data_chunk_{i}",
                            file_type="csv",
                        )
                except Exception as e:
                    logging.error(f"🚨 Error during file operation: {e}")
                finally:
                    if os.path.exists(temp_file.name):  # 파일이 존재하는지 확인
                        os.unlink(temp_file.name)  # 임시 파일 삭제

            logging.info("✔️ Data upload complete.")

    start = EmptyOperator(task_id="start")

    end = EmptyOperator(task_id="transform_end")

    slack_alert = SlackAlert(channel="#lulu-airflow-alert")

    wait_for_get_riot_api_dag = ExternalTaskSensor(
        task_id="wait_for_get_riot_api_dag",
        external_dag_id="get_riot_api",
        external_task_id="end",
        timeout=600,
        mode="poke",
        dag=dag,
    )

    transform_match_data = PythonOperator(
        task_id="transform_match_data",
        python_callable=transform_match_data,
        retries=3,  # 실패한 작업 3회 재시도
        retry_delay=timedelta(minutes=5),  # 각 재시도 사이의 5분 지연 시간
        execution_timeout=timedelta(minutes=60),  # 작업이 60분 초과하면 실패로 간주
        on_success_callback=slack_alert.slack_success_alert,
        on_failure_callback=slack_alert.slack_failure_alert,
        dag=dag,
    )

    transform_mastery_data = PythonOperator(
        task_id="transform_mastery_data",
        python_callable=transform_mastery_data,
        retries=3,
        retry_delay=timedelta(minutes=5),
        execution_timeout=timedelta(minutes=60),
        on_success_callback=slack_alert.slack_success_alert,
        on_failure_callback=slack_alert.slack_failure_alert,
        dag=dag,
    )

    (
        start
        >> wait_for_get_riot_api_dag
        >> transform_match_data
        >> transform_mastery_data
        >> end
    )
