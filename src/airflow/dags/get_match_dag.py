from airflow import DAG
from airflow.decorators import task
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime
from utils.match_list import match_list # 임시 match_list

with DAG(
    dag_id = 'get_match_dag',
    schedule_interval=None,
    start_date = datetime(2023, 8, 11),
    catchup=False,
) as dag:
    
    start = DummyOperator(task_id='start')
    
    @task()
    def check_and_store_duplicate(match_ids):
        from dotenv import load_dotenv
        import redis
        import os

        load_dotenv()    
        redis_host = os.environ.get('redis_host')
        redis_port = os.environ.get('redis_port')
        redis_client = redis.Redis(host=redis_host, port=redis_port)

        redis_key = 'match_ids'
        non_duplicates = []

        for match_id in match_ids:
            is_duplicate = redis_client.sismember(redis_key, match_id)

            if not is_duplicate:
                redis_client.sadd(redis_key, match_id)
                non_duplicates.append(match_id)

        return non_duplicates
    
    @task()
    def extract_match_data(match_ids):
        from dotenv import load_dotenv
        from utils.riot_util import get_match_details
        import pandas as pd
        import time
        import os

        load_dotenv()

        api_key = os.environ.get('api_key')

        data = {'match_id': [], 'teamId': [], 'position': [], 'kills': [], 'deaths': [], 'assists': [], 'win': [], 'championName': [], 'championId': [], 'patch': []}
        total_df = pd.DataFrame(data)

        for match_id in match_ids:
            match_details = get_match_details(match_id, api_key)

            teamId = [participant['teamId'] for participant in match_details['info']['participants']]
            teamPosition = [participant['teamPosition'] for participant in match_details['info']['participants']]
            kills = [participant['kills'] for participant in match_details['info']['participants']]
            deaths = [participant['deaths'] for participant in match_details['info']['participants']]
            assists = [participant['assists'] for participant in match_details['info']['participants']]
            win = [participant['win'] for participant in match_details['info']['participants']]
            championName = [participant['championName'] for participant in match_details['info']['participants']]
            championId = [participant['championId'] for participant in match_details['info']['participants']]
            patch = (match_details['info']['gameVersion'])[:5]

            data = {'match_id': [], 'teamId': [], 'position': [], 'kills': [], 'deaths': [], 'assists': [], 'win': [], 'championName': [], 'championId': [], 'patch': []}
            for i in range(10):
                data['match_id'].append(match_id)
                data['teamId'].append(teamId[i])
                data['position'].append(teamPosition[i])
                data['kills'].append(kills[i])
                data['deaths'].append(deaths[i])
                data['assists'].append(assists[i])
                data['win'].append(win[i])
                data['championName'].append(championName[i])
                data['championId'].append(championId[i])
                data['patch'].append(patch)

            df = pd.DataFrame(data)
            total_df = pd.concat([total_df, df], ignore_index=True)
            time.sleep(0.9)

        return total_df
    
    @task()
    def upload_to_s3(total_df):
        from dotenv import load_dotenv
        import pandas as pd
        import os
        import boto3

        load_dotenv()

        aws_access_key_id = os.environ.get('aws_access_key_id')
        aws_secret_access_key = os.environ.get('aws_secret_access_key')
        bucket_name = os.environ.get('bucket_name')
        s3_folder = os.environ.get('s3_folder')

        existing_df = None
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        try:
            response = s3.get_object(Bucket=bucket_name, Key=f'{s3_folder}/data.csv')
            existing_df = pd.read_csv(response['Body'])
        except Exception as e:
            pass

        # 데이터 병합 및 업로드
        if existing_df is not None:
            updated_df = pd.concat([existing_df, total_df], ignore_index=True)
        else:
            updated_df = total_df

        temp_csv_path = 'dags/temp_data.csv'
        updated_df.to_csv(temp_csv_path, index=False)
        s3.upload_file(temp_csv_path, bucket_name, f'{s3_folder}/data.csv')
        os.remove(temp_csv_path)

    check_and_store_task = check_and_store_duplicate(match_list)
    extract_match_data_task = extract_match_data(check_and_store_task)
    upload_to_s3_task = upload_to_s3(extract_match_data_task)

    end = DummyOperator(task_id='end')

    start >> check_and_store_task >> extract_match_data_task >> upload_to_s3_task >> end

