import logging
from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator


with DAG(
    dag_id="combine_match",
    schedule_interval=None,
    # schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 8, 17),
    catchup=False,
) as dag:

    @task()
    def get_match():
        import boto3
        import pandas as pd
        from airflow.models import Variable
        from io import StringIO

        aws_access_key_id = Variable.get("aws_access_key_id")
        aws_secret_access_key = Variable.get("aws_secret_access_key")
        bucket_name = Variable.get("bucket_name")

        current_date = datetime.now().strftime("%Y-%m-%d")

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="data/match/")
        all_files = [
            obj["Key"] for obj in response["Contents"] if obj["Key"].endswith(".csv")
        ]
        final_df = pd.DataFrame()

        for file in all_files:
            logging.info(file)
            csv_obj = s3_client.get_object(Bucket=bucket_name, Key=file)
            body = csv_obj["Body"].read().decode("utf-8")
            temp_df = pd.read_csv(StringIO(body))
            final_df = pd.concat([final_df, temp_df])

        final_csv_buffer = StringIO()
        final_df.to_csv(final_csv_buffer, index=False)
        s3_client.put_object(
            Bucket=bucket_name,
            Body=final_csv_buffer.getvalue(),
            Key=f"data/adhoc_match/{current_date}/merged.csv",
        )

    start = EmptyOperator(task_id="start")

    get_match_task = get_match()

    end = EmptyOperator(task_id="end")

    start >> get_match_task >> end
