from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from dotenv import load_dotenv
from utils.riot_util import get_match_details
import os
import pandas as pd
import redis
import time
from utils.match_list import match_list

load_dotenv()

api_key = os.environ.get('api_key')

# Connect to Redis server
redis_host = 'redis'
redis_port = 6379
redis_client = redis.Redis(host=redis_host, port=redis_port)

def check_and_store_duplicate(match_ids):
    redis_key = 'processed_match_ids'
    non_duplicates = []

    for match_id in match_ids:
        is_duplicate = redis_client.sismember(redis_key, match_id)

        if not is_duplicate:
            redis_client.sadd(redis_key, match_id)
            non_duplicates.append(match_id)

    print("Non-duplicate match IDs:", non_duplicates)
    return non_duplicates

def extract_match_data(**kwargs):
    match_ids = kwargs['task_instance'].xcom_pull(task_ids='check_and_store_task')
    api_key = os.environ.get('api_key')

    for match_id in match_ids:
        match_details = get_match_details(match_id, api_key)

        teamId = [participant['teamId'] for participant in match_details['info']['participants']]
        teamPosition = [participant['teamPosition'] for participant in match_details['info']['participants']]
        champion_names = [participant['championName'] for participant in match_details['info']['participants']]
        win = [participant['win'] for participant in match_details['info']['participants']]
        patch = (match_details['info']['gameVersion'])[:5]

        teams = {}
        for i, team_id in enumerate(teamId):
            if team_id not in teams:
                teams[team_id] = {'TOP': [], 'JUNGLE': [], 'MIDDLE': [], 'BOTTOM': [], 'UTILITY': [], 'win': win[i], 'patch': patch}
            position = teamPosition[i]
            teams[team_id][position].append(champion_names[i])

        data = {'match_id': [], 'teamId': [], 'TOP': [], 'JUNGLE': [], 'MIDDLE': [], 'BOTTOM': [], 'SUPPORT': [], 'win': [], 'patch': []}
        for team_id, team_data in teams.items():
            data['match_id'].append(match_id)
            data['teamId'].append(team_id)
            data['TOP'].append(team_data['TOP'][0])
            data['JUNGLE'].append(team_data['JUNGLE'][0])
            data['MIDDLE'].append(team_data['MIDDLE'][0])
            data['BOTTOM'].append(team_data['BOTTOM'][0])
            data['SUPPORT'].append(team_data['UTILITY'][0])
            data['win'].append(team_data['win'])
            data['patch'].append(team_data['patch'])
            print(data)

        file_path = 'dags/data.csv'
        df = pd.DataFrame(data)
        if os.path.exists(file_path):
            existing_df = pd.read_csv(file_path)
            updated_df = pd.concat([existing_df, df], ignore_index=True)
        else:
            updated_df = df

        updated_df.to_csv(file_path, index=False)
        time.sleep(0.9)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 10),
    'retries': 1,
}

dag = DAG('get_match_dag', default_args=default_args, schedule_interval=None)

check_and_store_task = PythonOperator(
    task_id='check_and_store_task',
    python_callable=check_and_store_duplicate,
    op_args=[match_list],
    dag=dag,
)

extract_match_data_task = PythonOperator(
    task_id='extract_match_data_task',
    python_callable=extract_match_data,
    provide_context=True,
    dag=dag,
)

check_and_store_task >> extract_match_data_task
