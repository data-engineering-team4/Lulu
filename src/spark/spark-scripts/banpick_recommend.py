import json
import boto3
import time
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import uuid
from pyspark.sql.types import StringType
from pyspark.sql import Row


def fetch_from_s3(bucket, key):
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read().decode("utf-8")


def fetch_sql_from_s3(bucket, query_key_list):
    query_list = []
    for query_key in query_key_list:
        key = "query/recommend/" + query_key
        query_list.append(fetch_from_s3(bucket, key))
    return query_list


def get_operator(value):
    if value == "???":
        return ">="
    else:
        return ">"


def generate_uuid():
    return str(uuid.uuid4())


def process_team_data(team, query_list, my_lane, flag):
    find_team_query = query_list[0]
    filter_team_query = query_list[1]
    team_summary_query = query_list[2]

    top_champ = team.get("TOP", "???")
    jungle_champ = team.get("JUNGLE", "???")
    middle_champ = team.get("MIDDLE", "???")
    bottom_champ = team.get("BOTTOM", "???")
    utility_champ = team.get("UTILITY", "???")

    matching_games = spark.sql(
        find_team_query.format(
            top_champ=top_champ,
            jungle_champ=jungle_champ,
            middle_champ=middle_champ,
            bottom_champ=bottom_champ,
            utility_champ=utility_champ,
            top_operator=get_operator(top_champ),
            jungle_operator=get_operator(jungle_champ),
            middle_operator=get_operator(middle_champ),
            bottom_operator=get_operator(bottom_champ),
            utility_operator=get_operator(utility_champ),
        )
    )
    if flag == 0:
        matching_games.createOrReplaceTempView("our_matching_games")
        filtered_data = spark.sql(filter_team_query)
        filtered_data.createOrReplaceTempView("our_filtered_data")
    else:
        matching_games.createOrReplaceTempView("opponent_matching_games")
        filtered_data = spark.sql(filter_team_query)
        filtered_data.createOrReplaceTempView("opponent_filtered_data")

    team_summary = spark.sql(team_summary_query.format(my_lane=my_lane))

    if team_summary.count() == 0:
        team_summary = spark.createDataFrame(
            [Row(champion_name="!!!", win_rate="!!!", pick_rate="!!!")]
        )

    team_summary = team_summary.withColumn("my_lane", F.lit(my_lane))

    champion_positions = {
        "top": top_champ,
        "jungle": jungle_champ,
        "middle": middle_champ,
        "bottom": bottom_champ,
        "utility": utility_champ,
    }

    for position, champ in champion_positions.items():
        team_summary = team_summary.withColumn(position, F.lit(champ))

    generate_uuid_udf = F.udf(generate_uuid, StringType())
    team_summary = team_summary.withColumn("id", generate_uuid_udf())

    if flag == 0:
        team_summary.write.jdbc(
            jdbc_url, "our_team", mode="append", properties=properties
        )

    else:
        team_summary.write.jdbc(
            jdbc_url, "opponent_team", mode="append", properties=properties
        )

    team_summary_pd = team_summary.toPandas()
    team_summary_json = team_summary_pd.to_json()
    team_summary_bytes = bytes(team_summary_json, encoding='utf-8')

    response = client.put_record(
        StreamName="sparktobackend",
        Data=team_summary_bytes,
        PartitionKey="partition_key"
    )

def recommend(my_lane, our_team, opponent_team, table_check):
    data_spark.createOrReplaceTempView("games")

    if our_team and "2" in table_check:
        process_team_data(our_team, query_list[:3], my_lane, 0)

    if opponent_team and "3" in table_check:
        opponent_champ = opponent_team.get(my_lane, "???")
        if opponent_champ != "???" and "4" in table_check:
            find_opponent_lane_query = query_list[8]
            filter_opponent_lane_query = query_list[9]
            counter_team_summary_query = query_list[10]

            matching_games = spark.sql(
                find_opponent_lane_query.format(my_lane=my_lane, champ=opponent_champ)
            )
            matching_games.createOrReplaceTempView("opponent_lane_matching_games")
            filtered_data = spark.sql(filter_opponent_lane_query)
            filtered_data.createOrReplaceTempView("opponent_lane_filtered_data")
            team_summary = spark.sql(counter_team_summary_query.format(my_lane=my_lane))
            if team_summary.count() == 0:
                team_summary = spark.createDataFrame(
                    [Row(champion_name="!!!", win_rate="!!!", pick_rate="!!!")]
                )
            team_summary = team_summary.withColumn("my_lane", F.lit(my_lane))
            generate_uuid_udf = F.udf(generate_uuid, StringType())
            team_summary = team_summary.withColumn("id", generate_uuid_udf())
            team_summary = team_summary.withColumn(
                "opponent_champ", F.lit(opponent_champ)
            )
            team_summary.write.jdbc(
                jdbc_url, "opponent_lane", mode="append", properties=properties
            )
            team_summary_pd = team_summary.toPandas()
            team_summary_json = team_summary_pd.to_json()
            team_summary_bytes = bytes(team_summary_json, encoding='utf-8')

            response = client.put_record(
                StreamName="sparktobackend",
                Data=team_summary_bytes,
                PartitionKey="partition_key"
            )

        process_team_data(opponent_team, query_list[3:6], my_lane, 1)

    if our_team and opponent_team and "1" in table_check:
        filter_all_team_query = query_list[6]
        all_team_summary_query = query_list[7]

        all_filtered_data = spark.sql(filter_all_team_query)
        all_filtered_data.createOrReplaceTempView("combined_filtered_data")
        all_filtered_data.show()

        all_team_summary = spark.sql(all_team_summary_query.format(my_lane=my_lane))
        if all_team_summary.count() == 0:
            all_team_summary = spark.createDataFrame(
                [Row(champion_name="!!!", win_rate="!!!", pick_rate="!!!")]
            )

        positions = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]

        for position in positions:
            champ = our_team.get(position, "???")
            all_team_summary = all_team_summary.withColumn(
                f"our_{position.lower()}", F.lit(champ)
            )

            champ = opponent_team.get(position, "???")
            all_team_summary = all_team_summary.withColumn(
                f"opponent_{position.lower()}", F.lit(champ)
            )

        all_team_summary = all_team_summary.withColumn("my_lane", F.lit(my_lane))
        generate_uuid_udf = F.udf(generate_uuid, StringType())
        all_team_summary = all_team_summary.withColumn("id", generate_uuid_udf())
        all_team_summary.write.jdbc(
            jdbc_url, "all_team", mode="append", properties=properties
        )
        all_team_summary_pd = all_team_summary.toPandas()
        all_team_summary_json = all_team_summary_pd.to_json()
        all_team_summary_bytes = bytes(all_team_summary_json, encoding='utf-8')

        response = client.put_record(
            StreamName="sparktobackend",
            Data=all_team_summary_bytes,
            PartitionKey="partition_key"
        )


if __name__ == "__main__":
    spark = SparkSession.builder.appName("BanPick").getOrCreate()

    # s3 연결
    s3_client = boto3.client("s3")
    adhoc_bucket_name = "de-4-2"
    query_bucket_name = "de-4-2-spark"

    adhoc_data_path = f"s3://{adhoc_bucket_name}/data/adhoc_match/merged.csv"
    data_spark = spark.read.csv(
        adhoc_data_path, header=True, inferSchema=True
    ).repartition(8)

    check_start = time.time()
    query_key_list = [
        "find_our_team.sql",
        "filter_our_team.sql",
        "recommend_our_team.sql",
        "find_opponent_team.sql",
        "filter_opponent_team.sql",
        "recommend_opponent_team.sql",
        "filter_all_team.sql",
        "recommend_all_team.sql",
        "find_opponent_lane.sql",
        "filter_opponent_lane.sql",
        "recommend_opponent_lane.sql",
    ]

    query_list = fetch_sql_from_s3(query_bucket_name, query_key_list)

    # secret manager 연결
    secret_name = "de-4-2-emr-secret-manager"
    region_name = "ap-northeast-3"

    sm_session = boto3.session.Session()
    sm_client = sm_session.client(
        service_name="secretsmanager", region_name=region_name
    )
    get_secret_value_response = sm_client.get_secret_value(SecretId=secret_name)
    secret_string = get_secret_value_response["SecretString"]
    secret_data = json.loads(secret_string)

    db_url = secret_data["jdbc_url"]
    db_user = secret_data["user"]
    db_password = secret_data["password"]

    # rds 연결
    jdbc_url = db_url

    properties = {
        "user": db_user,
        "password": db_password,
        "driver": "com.mysql.jdbc.Driver",
    }

    # kinesis 연결
    client = boto3.client("kinesis")
    stream_name = "de-4-2-stream"
    consumer_name = "de42"

    shard_iterator = client.get_shard_iterator(
        StreamName=stream_name,
        ShardId="shardId-000000000001",
        ShardIteratorType="LATEST",
    )["ShardIterator"]

    print("ready!!!!!!!!!!!!!!!!!!!!!!!!")
    while True:
        response = client.get_records(ShardIterator=shard_iterator, Limit=100)

        for record in response["Records"]:
            data = record["Data"].decode("utf-8")
            data_dict = json.loads(data)
            my_lane = data_dict["myLane"]
            our_team = data_dict["ourTeam"]
            opponent_team = data_dict["opponentTeam"]
            table_check = data_dict["table_check"]

            recommend(my_lane, our_team, opponent_team, table_check)

        shard_iterator = response["NextShardIterator"]

        time.sleep(1)
