from airflow import DAG
from airflow.decorators import task
from datetime import datetime

with DAG(
    dag_id = 'get_mastery',
    schedule_interval=None,
    start_date = datetime(2023,8,8),
    catchup=False,
) as dag:
    def create_champion_mastery_dateframe():
        """
        현재 db에 저장된 puuid들의 champion_mastery를 불러온뒤, csv로 저장.
        """
        import json
        import pandas as pd
        import numpy as np

        mysql_connection = connect_to_mysql()
        puuids = get_all_puuid(mysql_connection)

        with open("../analysis/champion_dictionary.json", "r") as f:
            champion_dict = json.load(f)

        columns = [f"{champion}" for champion in champion_dict.values() for suffix in
                   ['championPoints']]
        # ['championLevel']

        df = pd.DataFrame(columns=['puuid'] + columns, dtype=np.int64)
        df.set_index('puuid', inplace=True)

        for pid in puuids:
            champion_data = get_champion_mastery_by_puuid(pid, api_key)
            time.sleep(1)
            for champion in champion_data:
                champion_name = champion_dict[str(champion['championId'])]
                df.at[pid, champion_name] = champion['championPoints']

        df.fillna(0, inplace=True)
        df.to_csv('../analysis/champion_mastery_dataframe.csv', index=False)
        mysql_connection.close()


    @task()
    def dd():
        from kafka import KafkaProducer
        import json

        kafka_bootstrap_servers = "localhost:29092"
        kafka_topic = "summonersId"

        producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers,
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))

        data = 'Hello'
        producer.send(kafka_topic, data)
        producer.flush()
        producer.close()

    @task()
    def get_mastery_example():
        from kafka import KafkaConsumer

        kafka_bootstrap_servers = "localhost:29092"
        kafka_topic = "summonersId"

        consumer = KafkaConsumer(
            kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
            value_deserializer=lambda x: x.decode('utf-8')
        )

        for message in consumer:
            print(message.value)

    dd() >> get_mastery_example()