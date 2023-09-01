from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="get_champion_tier",
    schedule_interval=None,
    # schedule_interval=timedelta(days=14),
    start_date=datetime(2023, 8, 29),
    catchup=False,
) as dag:

    @task
    def get_champion_tier():
        from utils.common_util import download_from_s3
        import pandas as pd
        import logging

        # S3에서 파일 다운로드
        logging.info("📥 Downloading csv files from S3...")
        csv_files = download_from_s3("match", ".csv")

        if csv_files:
            logging.info(f"🔍 Found {len(csv_files)} csv files.")

            # 파일 병합
            logging.info("🔄 Merging csv files...")
            dataframes = {}  # 각 CSV 파일의 내용을 저장할 빈 딕셔너리

            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    dataframes[csv_file] = df
                    logging.info(
                        f"🚀Successfully read {csv_file}.")
                except Exception as e:
                    logging.error(
                        f"🚨Failed to read a csv file {csv_file} due to {e}"
                    )

            origin_df = pd.concat(dataframes)
            logging.info(f"🚀Successfully concat csv_files. Origin DataFrame shape: {origin_df.shape}.")



    start = EmptyOperator(task_id="start")

    end = EmptyOperator(task_id="end")

    start >> end