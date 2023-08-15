from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

def get_summoner_puuid(**kwargs):

    from utils.riot_util import get_puuid_by_id
    import time
    import json
    import logging
    from airflow.models import Variable
    from kafka import KafkaConsumer

    logging.basicConfig(level=logging.INFO)

    time.sleep(100)
    # TODO API_KEY Airflow에서 가져옴 -> AWS Secrets Manager로 대체하기
    api_key = Variable.get("RIOT_KEY_1")

    consumer = KafkaConsumer('summoner_data',
                             bootstrap_servers='kafka:9092',
                             value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                             group_id='group1')
    # summoner_data_list = json.loads(summoner_data_list_json) if summoner_data_list_json else []

    # logging.info(f'Challenger Summoner를 가져왔습니다. {len(summoner_data_list)}')

    request_count = 0
    for message in consumer:
        summoner = message.value
        logging.info(summoner)
        if summoner == 'finish':
            break
        if request_count >= 20:
            time.sleep(1.2)
            request_count = 0

        puuid = None
        retries = 3
        while retries > 0:
            try:
                puuid = get_puuid_by_id(summoner['summoner_id'], api_key)
                if puuid:
                    break
            except Exception as e:
                logging.error(f"Error fetching puuid for {summoner['summoner_name']}: {e}")
                retries -= 1
                time.sleep(1.2)  # 재시도 전에 시간 간격 주기

        if puuid:
            summoner['puuid'] = puuid
        else:
            logging.error(f"Failed to fetch puuid for {summoner['summoner_name']} after retries")

        request_count += 1

    # logging.info(f"Success to get puuid data : {len(summoner_data_list)}")

    # return summoner_data_list[:10]

with DAG(
        dag_id='get_summoner_puuid',
        schedule_interval=None,
        start_date=datetime(2023, 8, 10),
        catchup=False,
) as dag:

    start = EmptyOperator(
        task_id='start'
    )

    end = EmptyOperator(
        task_id='end'
    )

    get_summoner_puuid_op = PythonOperator(
        task_id='get_summoner_puuid',
        python_callable=get_summoner_puuid,
        provide_context=True,
    )

    trigger_get_match_list_dag = TriggerDagRunOperator(
        task_id='trigger_get_match_list_dag',
        trigger_dag_id='get_match_list',
    )

    start >> get_summoner_puuid_op >> trigger_get_match_list_dag >> end
