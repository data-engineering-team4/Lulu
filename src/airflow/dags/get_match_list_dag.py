from airflow import DAG
import datetime
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator


with DAG(
    dag_id='get_match_list',
    schedule_interval=None,
    start_date=datetime.datetime(2023, 8, 10),
    catchup=False,
) as dag:

    start = EmptyOperator(
        task_id='start'
    )

    end = EmptyOperator(
        task_id='end'
    )

    def get_match_list(**context):

        from utils.riot_util import get_match_history
        import time
        import logging
        from airflow.models import Variable

        logging.basicConfig(level=logging.INFO)

        # TODO API_KEY Airflow에서 가져옴 -> AWS Secrets Manager로 대체하기
        api_key = Variable.get("RIOT_KEY_1")

        # 7일 전의 datetime
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        seven_days_ago_in_ms = int(seven_days_ago.timestamp() * 1000)

        summoner_data_list = context['dag_run'].conf['summoner_data_list']
        logging.info(f'puuid data list를 가져왔습니다. {len(summoner_data_list)}')

        request_count = 0
        for summoner in summoner_data_list:
            if request_count >= 20:
                logging.info('Rate limit reached, sleeping for 1.2 seconds.')
                time.sleep(1.2)
                request_count = 0

            puuid = summoner['puuid']
            retries = 3
            while retries > 0:
                try:
                    match_list = get_match_history(puuid, seven_days_ago_in_ms, 1, 100, api_key)
                    summoner['match_id_list'] = match_list
                    break
                except Exception as e:
                    logging.error(f"Error fetching match list for {puuid}: {e}")
                    retries -= 1
                    time.sleep(1.2)

            if retries == 0:
                logging.error(f"Failed to fetch match list for {puuid} after retries")

            request_count += 1

        logging.info(f'Success to get match list data for {len(summoner_data_list)} summoners.')

        return summoner_data_list


    get_match_list_op = PythonOperator(
        task_id='get_match_list',
        python_callable=get_match_list,
    )

    start >> get_match_list_op >> end