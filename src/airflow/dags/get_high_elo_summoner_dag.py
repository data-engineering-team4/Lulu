from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.dummy_operator import DummyOperator

with DAG(
    dag_id = 'get_high_elo_summoners_by_tier',
    schedule_interval=None,
    # schedule_interval=timedelta(days=7),
    start_date = datetime(2023,8,8),
    catchup=False,
) as dag:

    start = DummyOperator(task_id='start')

    @task()
    def get_high_elo_summoners_by_tier():

        from utils.riot_util import get_high_elo_summoner_info
        import time
        import logging
        from dotenv import load_dotenv
        import os

        logging.basicConfig(level=logging.INFO)

        load_dotenv()
        api_key = os.getenv("API_KEY")

        high_elo_list = ["challenger", "grandmaster", "master"]
        summoner_data_list = []

        for high_elo in high_elo_list:
            json_data = get_high_elo_summoner_info(high_elo, api_key)

            for data in json_data['entries']:
                summoner_data_list.append({
                    'high_elo': high_elo,
                    'summoner_id': data['summonerId'],
                    'summoner_name': data['summonerName'],
                })

            time.sleep(1.2)

        return summoner_data_list


    get_high_elo_summoners = get_high_elo_summoners_by_tier()

    trigger_get_puuid_dag = TriggerDagRunOperator(
        task_id='trigger_get_puuid_dag',
        trigger_dag_id='get_summoner_puuid',
    )

    end = DummyOperator(task_id='end')

    start >> get_high_elo_summoners >> trigger_get_puuid_dag >> end