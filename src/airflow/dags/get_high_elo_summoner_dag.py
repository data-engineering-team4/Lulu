import json

from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


with DAG(
    dag_id = 'get_high_elo_summoners_by_tier',
    schedule_interval=None,
    # schedule_interval=timedelta(days=7),
    start_date=datetime(2023, 8, 9),
    catchup=False,
) as dag:

    start = EmptyOperator(task_id='start')

    def get_high_elo_summoners_by_tier(**context):

        from utils.riot_util import get_high_elo_summoner_info
        import time
        import logging
        from airflow.models import Variable

        logging.basicConfig(level=logging.INFO)

        # TODO API_KEY Airflow에서 가져옴 -> AWS Secrets Manager로 대체하기
        api_key = Variable.get("RIOT_KEY_1")

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

    def push_summoner_data_to_xcom(**context):
        summoner_data_list = get_high_elo_summoners_by_tier(**context)
        context['task_instance'].xcom_push(key='summoner_data_list', value=json.dumps(summoner_data_list))
        return summoner_data_list


    push_summoner_data_to_xcom_op = PythonOperator(
        task_id='push_summoner_data_to_xcom',
        python_callable=push_summoner_data_to_xcom,
        provide_context=True,
        dag=dag
    )

    trigger_get_puuid_dag = TriggerDagRunOperator(
        task_id='trigger_get_puuid_dag',
        trigger_dag_id='get_summoner_puuid',
    )

    end = EmptyOperator(task_id='end')

    start >> push_summoner_data_to_xcom_op >> trigger_get_puuid_dag >> end