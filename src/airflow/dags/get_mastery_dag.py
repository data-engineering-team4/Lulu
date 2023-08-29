from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="get_mastery",
    schedule_interval=None,
    # schedule_interval=timedelta(days=14),
    start_date=datetime(2023, 8, 29),
    catchup=False,
) as dag:

    start = EmptyOperator(task_id="start")

    @task()
    def get_mastery():
        import boto3
        import pandas as pd
        import os
        from io import BytesIO
        import json
        from utils.common_util import get_formatted_date
        from datetime import datetime, timedelta
        from airflow.models import Variable
        from pytz import timezone

        aws_access_key_id = Variable.get("aws_access_key_id")
        aws_secret_access_key = Variable.get("aws_secret_access_key")
        bucket_name = Variable.get("bucket_name")

        s3_client = boto3.client("s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        tz = timezone('Asia/Seoul')
        end_date = datetime.now(tz)
        start_date = end_date - timedelta(days=14)
        date_range = pd.date_range(start_date, end_date)

        combined_dfs = []

        for date in date_range[:-1]:
            YMD = get_formatted_date(date)
            
            for data_file_number in range(1, 4):
                file_key = f"data/mastery/{YMD}/data{data_file_number}.csv"
                
                try:
                    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
                    content = response["Body"].read()

                    csv_data = BytesIO(content)
                    csv_df = pd.read_csv(csv_data, encoding='utf-8', usecols=lambda column: column != 'id')

                    combined_dfs.append(csv_df)

                    print(f"Processed: {YMD}, data{data_file_number}.csv")

                except s3_client.exceptions.NoSuchKey:
                    print(f"File not found: {YMD}, data{data_file_number}.csv")

        if combined_dfs:
            final_combined_df = pd.concat(combined_dfs, ignore_index=True)

        directory = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(directory, "utils/champion_dictionary.json")

        with open(json_file_path, "r", encoding="utf-8") as json_file:
            champion_dict = json.load(json_file)

        columns = list(champion_dict.values())
        final_combined_df.rename(columns={old_column: new_column for old_column, new_column in zip(final_combined_df.columns, columns)}, inplace=True)



        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.preprocessing import StandardScaler

        num_champions = 10

        json_file_path = os.path.join(directory, "utils/champion_mapping_ko_en.json")
        with open(json_file_path, "r", encoding="utf-8") as f:
                champion_mapping_ko_en = json.load(f)
        champion_mapping_en_kr = {value: key for key, value in champion_mapping_ko_en.items()}

        scaler = StandardScaler()
        df = pd.DataFrame(scaler.fit_transform(final_combined_df), columns=final_combined_df.columns)

        df_transposed = df.transpose()

        cosine_sim = cosine_similarity(df_transposed)
        cosine_sim_df = pd.DataFrame(cosine_sim, index=df.columns, columns=df.columns)

        similar_champions_dict = {}

        for champion_name in champion_mapping_ko_en:
            champion = champion_mapping_ko_en[champion_name]
            similar_champs = cosine_sim_df[champion].sort_values(ascending=False)[1:num_champions + 1]
            similar_champs_list = similar_champs.index.map(champion_mapping_en_kr).tolist()
            similar_champions_dict[champion_name] = similar_champs_list

        similar_champions_json_path = os.path.join(directory, "similar_champions.json")
        with open(similar_champions_json_path, "w", encoding="utf-8") as json_file:
            json.dump(similar_champions_dict, json_file, ensure_ascii=False, indent=4)

        new_df = pd.DataFrame(columns=["champion_name"] + list(range(1, num_champions + 1)))

        for champion_name, similar_champs_list in similar_champions_dict.items():
            row_data = [champion_name] + similar_champs_list
            new_df.loc[len(new_df)] = row_data

        import pymysql

        host = Variable.get("host")
        user = Variable.get("user")
        password = Variable.get("password")
        database = Variable.get("database")

        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            with connection.cursor() as cursor:
                print("Connected to MySQL database.")

                delete_sql = "DELETE FROM mastery"
                cursor.execute(delete_sql)
                connection.commit()
                print("All records deleted from mastery table.")

                for row in new_df.iterrows():
                    champion_name = row[1]["champion_name"]
                    similar_champs_values = list(row[1][1:])
                    formatted_values = ', '.join([f'"{value}"' for value in similar_champs_values])
                    sql = f"INSERT INTO mastery (champion_name, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`) " \
                            f"VALUES ('{champion_name}', {formatted_values})"
                    cursor.execute(sql)
                
                connection.commit()
                print("Data inserted into MySQL table.")
                similar_champions_json_path = os.path.join(directory, "similar_champions.json")
    
                try:
                    os.remove(similar_champions_json_path)
                    print("Deleted similar_champions.json")
                except Exception as e:
                    print(f"Error deleting similar_champions.json: {str(e)}")

        finally:
            connection.close()

    end = EmptyOperator(task_id="end")
    get_mastery_task = get_mastery()
    start >> get_mastery_task >> end