import random

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from ..models.team_info import TeamInfo
from ..models.team import AllTeam, OurTeam, OpponentTeam, OpponentLane
from ..models.summoner_info import SummonerInfo
from ..models.summoner import get_champion_mastery_by_name
from ..db_session import SessionLocal
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import json
import boto3
from joblib import load
import pandas as pd
import numpy as np
from io import BytesIO
import time
from datetime import datetime

router = APIRouter()
load_dotenv()

kinesis_stream_name = os.environ.get("KINESIS_STREAM_NAME")
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

api_key = os.environ.get("RIOT_API_KEY_5")

client = boto3.client(
    "kinesis",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name="ap-northeast-3",
)
s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

response = s3_client.get_object(
    Bucket="de-4-2", Key="data/progamer/kmeans_model.joblib"
)
model_stream = BytesIO(response["Body"].read())
kmeans_model = load(model_stream)

response = s3_client.get_object(
    Bucket="de-4-2", Key="data/progamer/progamer_list_with_clusters.csv"
)
progamer_csv_stream = BytesIO(response["Body"].read())
progamer_df = pd.read_csv(progamer_csv_stream)


response = s3_client.get_object(
    Bucket="de-4-2", Key="data/progamer/index.csv"
)
index_csv_stream = BytesIO(response["Body"].read())
index_df = pd.read_csv(index_csv_stream, index_col=0)

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "champions.json"), "r") as f:
    champion_data = json.load(f)

champion_mapping = {}
for k, v in champion_data.items():
    champion_mapping[int(k)] = v

lane_mapping = {
    0: "ALL",
    1: "TOP",
    2: "JUNGLE",
    3: "MIDDLE",
    4: "BOTTOM",
    5: "UTILITY",
    6: "TOP",
    7: "JUNGLE",
    8: "MIDDLE",
    9: "BOTTOM",
    10: "UTILITY",
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/banpick/produce")
async def get_team_info(team_info: TeamInfo, db: Session = Depends(get_db)):
    current_time_milliseconds = datetime.utcnow()
    my_lane = lane_mapping.get(team_info.myLane + 1)
    our_team = {}
    opponent_team = {}
    table_check = []

    for lane, champ_id in team_info.ourTeam.items():
        new_lane = lane_mapping.get(int(lane))
        new_champ = champion_mapping.get(champ_id + 1)
        our_team[new_lane] = new_champ

    for lane, champ_id in team_info.opponentTeam.items():
        new_lane = lane_mapping.get(int(lane))
        new_champ = champion_mapping.get(champ_id + 1)
        opponent_team[new_lane] = new_champ

    all_team_check = (
        db.query(AllTeam)
        .filter_by(
            my_lane=my_lane,
            our_top=our_team.get("TOP", "???"),
            our_jungle=our_team.get("JUNGLE", "???"),
            our_middle=our_team.get("MIDDLE", "???"),
            our_bottom=our_team.get("BOTTOM", "???"),
            our_utility=our_team.get("UTILITY", "???"),
            opponent_top=opponent_team.get("TOP", "???"),
            opponent_jungle=opponent_team.get("JUNGLE", "???"),
            opponent_middle=opponent_team.get("MIDDLE", "???"),
            opponent_bottom=opponent_team.get("BOTTOM", "???"),
            opponent_utility=opponent_team.get("UTILITY", "???"),
        )
        .all()
    )
    if not all_team_check:
        table_check.append("1")

    all_team_check_dicts = [
        {"championName": row.champion_name} for row in all_team_check
    ]
    our_team_check_dicts = []
    opponent_team_check_dicts = []
    opponent_lane_check_dicts = []
    if our_team:
        our_team_check = (
            db.query(OurTeam)
            .filter_by(
                my_lane=my_lane,
                top=our_team.get("TOP", "???"),
                jungle=our_team.get("JUNGLE", "???"),
                middle=our_team.get("MIDDLE", "???"),
                bottom=our_team.get("BOTTOM", "???"),
                utility=our_team.get("UTILITY", "???"),
            )
            .all()
        )
        if not our_team_check:
            table_check.append("2")
        our_team_check_dicts = [
            {"championName": row.champion_name} for row in our_team_check
        ]

    if opponent_team:
        opponent_team_check = (
            db.query(OpponentTeam)
            .filter_by(
                my_lane=my_lane,
                top=opponent_team.get("TOP", "???"),
                jungle=opponent_team.get("JUNGLE", "???"),
                middle=opponent_team.get("MIDDLE", "???"),
                bottom=opponent_team.get("BOTTOM", "???"),
                utility=opponent_team.get("UTILITY", "???"),
            )
            .all()
        )
        if not opponent_team_check:
            table_check.append("3")
        opponent_team_check_dicts = [
            {"championName": row.champion_name} for row in opponent_team_check
        ]

    opponent_champ = opponent_team.get(my_lane, "???")
    if opponent_champ != "???":
        opponent_lane_check = (
            db.query(OpponentLane)
            .filter_by(
                my_lane=my_lane,
                opponent_champ=opponent_champ,
            )
            .all()
        )
        if not opponent_lane_check:
            table_check.append("4")
        opponent_lane_check_dicts = [
            {"championName": row.champion_name} for row in opponent_lane_check
        ]

    print("Received data:", my_lane, our_team, opponent_team)

    if my_lane != "ALL" and (our_team or opponent_team) and table_check:
        print("table_check", table_check)
        transformed_data = {
            "myLane": my_lane,
            "ourTeam": our_team,
            "opponentTeam": opponent_team,
            "table_check": table_check,
        }
        json_data = json.dumps(transformed_data)

        try:
            response = client.put_record(
                StreamName=kinesis_stream_name,
                Data=json_data,
                PartitionKey="partition_key",
            )
        except Exception as e:
            print("Kinesis Error", e)
            return {"error": str(e)}
    else:
        print("already process all")

    return {
        "table_check": table_check,
        "currentTimestamp": current_time_milliseconds,
        "all_team_check_dicts": all_team_check_dicts,
        "our_team_check_dicts": our_team_check_dicts,
        "opponent_team_check_dicts": opponent_team_check_dicts,
        "opponent_lane_check_dicts": opponent_lane_check_dicts,
    }


@router.post("/banpick/search")
async def get_summoner_name(summoner_info: SummonerInfo):
    print("Received data:", summoner_info)

    mastery_data = get_champion_mastery_by_name(summoner_info.summonerName, api_key)

    if 'id' in index_df.columns:
        index_df.drop(columns=['id'], inplace=True)

    df = pd.DataFrame(columns=index_df.columns)
    update_dict = {}
    for data in mastery_data:
        champion_id = str(data["championId"])
        champion_points = data["championPoints"]
        update_dict[champion_id] = champion_points

    puuid = mastery_data[0]['puuid']
    df.loc[puuid] = np.nan

    df.loc[puuid, update_dict.keys()] = update_dict.values()

    if df.isnull().values.any():
        df.fillna(0, inplace=True)

    champion_mastery_df = df.copy()

    if champion_mastery_df.isnull().values.any():
        champion_mastery_df.fillna(0, inplace=True)

    user_cluster = kmeans_model.predict(champion_mastery_df)
    recommended_progamer = progamer_df[progamer_df["cluster"] == user_cluster[0]]
    recommended_progamer = recommended_progamer.to_dict(orient='records')

    # 이름을 기반으로 시드 설정
    seed = sum(ord(char) for char in summoner_info.summonerName)

    # 시드 설정
    random.seed(seed)

    random_item = random.choice(recommended_progamer)

    print(f"✅ recommendedProgamer: {random_item}")

    return {
        "summonerName": summoner_info.summonerName,
        "championMastery": mastery_data,
        "recommendedProgamer": random_item,
    }


@router.post("/banpick/consume")
async def consume_team(request: Request):
    request_data = await request.json()
    timestamp = request_data["timestamp"]
    new_timestamp = timestamp.replace("T", " ")
    shard_iterator = client.get_shard_iterator(
        StreamName="sparktobackend",
        ShardId="shardId-000000000001",
        ShardIteratorType="AT_TIMESTAMP",
        Timestamp=new_timestamp,
    )["ShardIterator"]
    kinds_data_list = request_data["kinds"]
    print(kinds_data_list)
    result_list = []
    while True:
        response = client.get_records(ShardIterator=shard_iterator, Limit=100)

        for record in response["Records"]:
            data_str = record["Data"].decode("utf-8")
            data_json = json.loads(data_str)
            team_summary_received = data_json["team_summary"]
            extra_info_received = data_json["extra_info"]
            if extra_info_received in kinds_data_list:
                print(extra_info_received)
                kinds_data_list.remove(extra_info_received)
                result_list.append(
                    {extra_info_received: team_summary_received["champion_name"]}
                )
                if not kinds_data_list:
                    print(result_list)
                    print("finish")
                    return {"data": result_list}
        shard_iterator = response["NextShardIterator"]
        time.sleep(1)
