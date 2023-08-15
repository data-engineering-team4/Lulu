from airflow import DAG
from airflow.decorators import task
from airflow.operators.dummy import DummyOperator
from datetime import datetime
from utils.id_list import id_list # 임시 id_list

with DAG(
    dag_id = 'get_mastery_dag',
    schedule_interval=None,
    start_date = datetime(2023, 8, 15),
    catchup=False,
) as dag:
    
    # start = DummyOperator(task_id='start')
    
    @task()
    def get_champion_mastery(id_list):
        from dotenv import load_dotenv
        from utils.riot_util import get_champion_mastery_by_id
        import pandas as pd
        import time
        import os
        import json

        load_dotenv()
        api_key = os.environ.get('api_key')

        script_path = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(script_path, 'utils', 'champion_dictionary.json')

        with open(json_file_path, 'r') as json_file:
            json_data = json_file.read()

        champion_dict = json.loads(json_data)

        data = {'id': []}
        data.update({key: [] for key in champion_dict.keys() if key != 'id'})
        total_df = pd.DataFrame(data)

        for id in id_list:
            tmp = get_champion_mastery_by_id(id, api_key)
            champion_id = []
            champion_points = []
            for champion in tmp:
                champion_id.append(champion['championId'])
                champion_points.append(champion['championPoints'])

            data = {'id': []}
            data.update({key: [] for key in champion_dict.keys() if key != 'id'})

            data['id'].append(id)

            for i in range(len(champion_id)):
                if str(champion_id[i]) in data:
                    data[str(champion_id[i])].append(champion_points[i])
            
            for key in data.keys():
                if key != 'id' and not data[key]:
                    data[key].append(0)
            

            df = pd.DataFrame(data)
            total_df = pd.concat([total_df, df], ignore_index=True)
            time.sleep(1)
        
        return(total_df)
    
    @task()
    def upload_to_s3(total_df):
        from dotenv import load_dotenv
        from utils.common_util import get_current_datetime, get_formatted_date
        import os
        import boto3

        load_dotenv()

        aws_access_key_id = os.environ.get('aws_access_key_id')
        aws_secret_access_key = os.environ.get('aws_secret_access_key')
        bucket_name = os.environ.get('bucket_name')
        s3_folder = os.environ.get('s3_folder')
        NOW = get_current_datetime()
        YMD = get_formatted_date(NOW)


        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        temp_csv_path = 'dags/temp_data.csv'
        total_df.to_csv(temp_csv_path, index=False)
        s3.upload_file(temp_csv_path, bucket_name, f'{s3_folder}/mastery/{YMD}/data.csv')
        os.remove(temp_csv_path)

    get_champion_mastery_task = get_champion_mastery(id_list)
    upload_to_s3_task = upload_to_s3(get_champion_mastery_task)

    # end = DummyOperator(task_id='end')

    # start >> get_champion_mastery_task >> upload_to_s3_task >> end
    get_champion_mastery_task >> upload_to_s3_task

