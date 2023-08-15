from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

def get_high_elo_summoners_by_tier():

    from utils.riot_util import get_high_elo_summoner_info
    import time
    import logging
    from airflow.models import Variable
    import json
    from kafka import KafkaProducer

    logging.basicConfig(level=logging.INFO)

    producer = KafkaProducer(bootstrap_servers='kafka:9092')

    # TODO API_KEY Airflow에서 가져옴 -> AWS Secrets Manager로 대체하기
    api_key = Variable.get("RIOT_KEY_1")

    high_elo_list = ["challenger", "grandmaster", "master"]

    for high_elo in high_elo_list:
        json_data = get_high_elo_summoner_info(high_elo, api_key)
        # logging.info(json_data)
        for data in json_data['entries']:
            summoner_data = {
                'high_elo': high_elo,
                'summoner_id': data['summonerId'],
                'summoner_name': data['summonerName'],
            }
            value = json.dumps(summoner_data).encode('utf-8')
            producer.send('summoner_data', value=value)
        time.sleep(1.2)
    producer.send('summoner_data', value=json.dumps('finish').encode('utf-8'))
    producer.flush()

with DAG(
    dag_id = 'get_high_elo_summoners_by_tier',
    schedule_interval=None,
    # schedule_interval=timedelta(days=7),
    start_date=datetime(2023, 8, 9),
    catchup=False,
) as dag:

    start = EmptyOperator(task_id='start')

    get_high_elo_summoners_by_tier = PythonOperator(
        task_id='get_high_elo_summoners_by_tier',
        python_callable=get_high_elo_summoners_by_tier,
        provide_context=True,
    )

    trigger_get_puuid_dag = TriggerDagRunOperator(
        task_id='trigger_get_puuid_dag',
        trigger_dag_id='get_summoner_puuid',
    )

    end = EmptyOperator(task_id='end')

    start >> get_high_elo_summoners_by_tier >> trigger_get_puuid_dag >> end