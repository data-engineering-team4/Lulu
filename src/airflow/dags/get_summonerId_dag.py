from airflow import DAG
from airflow.decorators import task
from datetime import datetime

with DAG(
    dag_id = 'get_summoners_by_tier',
    schedule_interval=None,
    start_date = datetime(2023,8,8),
    catchup=False,
) as dag:
    @task()
    def get_summoners_by_tier():
        from dotenv import load_dotenv
        import os
        from utils.riot_util import get_summonerId_by_tier_division_page

        load_dotenv()
        api_key = os.environ.get("API_KEY")
