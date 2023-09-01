from fastapi import APIRouter, Depends
from ..models.team_info import TeamInfo
from ..models.summoner_info import SummonerInfo
from ..models.summoner import Summoner, create_summoner
from ..db_session import SessionLocal
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import json
import boto3

router = APIRouter()
load_dotenv()

kinesis_stream_name = os.environ.get("KINESIS_STREAM_NAME")
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

client = boto3.client(
    "kinesis",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name="ap-northeast-3",
)

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
async def get_team_info(team_info: TeamInfo):
    my_lane = lane_mapping.get(team_info.myLane + 1)
    our_team = {}
    opponent_team = {}

    for lane, champ_id in team_info.ourTeam.items():
        new_lane = lane_mapping.get(int(lane))
        new_champ = champion_mapping.get(champ_id + 1)
        our_team[new_lane] = new_champ

    for lane, champ_id in team_info.opponentTeam.items():
        new_lane = lane_mapping.get(int(lane))
        new_champ = champion_mapping.get(champ_id + 1)
        opponent_team[new_lane] = new_champ

    print("Received data:", my_lane, our_team, opponent_team)

    if my_lane != "ALL" and (our_team or opponent_team):
        print("good")
        transformed_data = {
            "myLane": my_lane,
            "ourTeam": our_team,
            "opponentTeam": opponent_team,
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

    return {"myLane": my_lane, "ourTeam": our_team, "opponentTeam": opponent_team}


@router.post("/banpick/search")
async def get_summoner_name(summoner_info: SummonerInfo, db: Session = Depends(get_db)):
    print("Received data:", summoner_info)
    db_summoner = Summoner(summonerName=summoner_info.summonerName)
    db_summoner = create_summoner(db, db_summoner)
    return {"summonerName": db_summoner.summonerName}
