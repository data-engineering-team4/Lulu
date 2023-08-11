from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.dummy_operator import DummyOperator

with DAG(
    dag_id = 'get_summoners_by_tier',
    schedule_interval=None,
    # schedule_interval=timedelta(days=1),
    start_date = datetime(2023,8,8),
    catchup=False,
) as dag:

    start = DummyOperator(task_id='start')

    @task()
    def get_summoners_by_tier():

        from utils.riot_util import get_summoner_info_by_tier_division_page
        import time
        import redis
        import logging
        from dotenv import load_dotenv
        import os

        logging.basicConfig(level=logging.INFO)

        load_dotenv()
        api_key = os.getenv("API_KEY")

        redis_host = 'redis'
        redis_port = 6379
        redis_client = redis.Redis(host=redis_host, port=redis_port)

        redis_key = 'processed_summoners_ids'
        processed_summoner_ids = set(redis_client.smembers(redis_key))
        logging.info("redis",len(processed_summoner_ids))

        tier_list = ["DIAMOND", "EMERALD", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
        division_list = ["I", "II", "III", "IV"]

        summoner_data_list = []
        days_since_start = (datetime.now() - datetime(2023, 8, 10)).days
        start_page = (days_since_start * 4) % 200 + 1
        end_page = start_page + 3

        for tier in tier_list:
            for division in division_list:
                for page in range(start_page, end_page + 1):
                    json_data = get_summoner_info_by_tier_division_page(tier, division, page, api_key)
                    for data in json_data:
                        summoner_id = data['summonerId']

                        if summoner_id not in processed_summoner_ids:
                            summoner_data_list.append({
                                'tier': tier,
                                'division': division,
                                'summoner_id': data['summonerId'],
                                'summoner_name': data['summonerName'],
                            })
                            redis_client.sadd(redis_key, summoner_id)
                            processed_summoner_ids.add(summoner_id)
                    time.sleep(1.2)

        return summoner_data_list

    get_summoners = get_summoners_by_tier()

    trigger_get_puuid_dag = TriggerDagRunOperator(
        task_id='trigger_get_puuid_dag',
        trigger_dag_id='get_summoner_puuid',
    )

    end = DummyOperator(task_id='end')

    start >> get_summoners >> trigger_get_puuid_dag >> end