import time

from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="get_progamer_mastery",
    schedule_interval=None,
    # schedule_interval=timedelta(days=14),
    start_date=datetime(2023, 8, 29),
    catchup=False,
) as dag:
    @task()
    def get_progamer_mastery(key_num):
        from utils.common_util import setup_task
        from utils.riot_util import get_champion_mastery_by_name
        import boto3
        from airflow.models import Variable
        from io import BytesIO
        import pandas as pd
        from sklearn.cluster import KMeans
        import numpy as np
        from joblib import dump, load

        api_key, redis_conn, logging = setup_task(key_num)

        aws_access_key_id = Variable.get("aws_access_key_id")
        aws_secret_access_key = Variable.get("aws_secret_access_key")
        bucket_name = Variable.get("bucket_name")

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        current_date = datetime.now()
        previous_dates = [current_date - timedelta(days=i) for i in range(1, 3)]
        formatted_dates = [date.strftime("%Y-%m-%d") for date in previous_dates]

        mastery_dfs = []
        # combine_mastery_data
        for date in formatted_dates:
            folder_name = f"data/mastery/{date}/"
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
            csv_files = [
                obj["Key"] for obj in response["Contents"] if obj["Key"].endswith(".csv")
            ]

            if csv_files:
                logging.info(f"🔍 Found {len(csv_files)} csv files.")

                for file in csv_files:
                    try:
                        logging.info(file)
                        resp = s3_client.get_object(Bucket=bucket_name, Key=file)
                        cont = resp["Body"].read()

                        csv_data = BytesIO(cont)
                        dataframe = pd.read_csv(csv_data, encoding='utf-8')

                        mastery_dfs.append(dataframe)

                        logging.info(
                            f"🚀Successfully read {file}. DataFrame shape: {dataframe.shape}"
                        )
                    except Exception as e:
                        logging.error(f"🚨Failed to read csv files due to {e} ")

        if mastery_dfs:
            mastery_df = pd.concat(mastery_dfs, ignore_index=True)

        # 프로 숙련도 데이터
        file_key = f"data/progamer/progamer_list.csv"
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        content = response["Body"].read()
        pro_name_csv_data = BytesIO(content)
        pro_name_df = pd.read_csv(
            pro_name_csv_data,
            encoding="utf-8",
            usecols=lambda column: column != "URL",
        )
        progamer_summoner_names = pro_name_df['nickname'].tolist()
        pro_puuids = {}
        pro_df = pd.DataFrame(columns=mastery_df.columns)
        for index, name in enumerate(progamer_summoner_names):
            try:
                mastery_data = get_champion_mastery_by_name(name, api_key)
                puuid = mastery_data[0]['puuid']
                pro_puuids[name] = puuid

                pro_df.loc[puuid] = None
                pro_df.loc[puuid, 'id'] = puuid
                for summoner_data in mastery_data:
                    champion_id = str(summoner_data['championId'])
                    champion_points = summoner_data['championPoints']
                    pro_df.at[puuid, champion_id] = champion_points

            except Exception as e:
                logging.error(f"🚨Failed to get mastery details: {e}")
                continue

        mastery_data = pd.concat([mastery_df, pro_df], ignore_index=True)
        mastery_data_clustering = mastery_data.drop(['Unnamed: 0', 'id'], axis=1)
        if mastery_data_clustering.isnull().values.any():
            mastery_data_clustering.fillna(0, inplace=True)
        n_clusters = 15
        kmeans = KMeans(n_clusters=n_clusters, random_state=0)
        kmeans.fit(mastery_data_clustering)
        mastery_data['cluster'] = kmeans.labels_

        result = {}
        for name in progamer_summoner_names:
            try:
                puuid = pro_puuids.get(name)
                print(puuid)
                user_data = mastery_data[mastery_data['id'] == puuid]
                user_cluster = user_data['cluster'].iloc[0]
                result[name] = user_cluster
            except Exception as e:
                logging.error("!!!!!!!!!!!!")
                print(e)
                continue
        print(pro_puuids)
        pro_name_df['cluster'] = pro_name_df['nickname'].map(result)
        csv_buffer = BytesIO()
        pro_name_df.to_csv(csv_buffer, index=False, encoding="utf-8")
        s3_client.put_object(Bucket=bucket_name, Key="data/progamer/progamer_list_with_clusters.csv",
                             Body=csv_buffer.getvalue())

        buffer = BytesIO()
        dump(kmeans, buffer)
        buffer.seek(0)
        s3_client.put_object(Bucket=bucket_name, Key="data/progamer/kmeans_model.joblib", Body=buffer.getvalue())

    start = EmptyOperator(task_id="start")

    get_progamer_mastery_task = get_progamer_mastery(5)

    end = EmptyOperator(task_id="end")

    start >> get_progamer_mastery_task >> end
