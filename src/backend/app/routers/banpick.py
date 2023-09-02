from fastapi import APIRouter, Depends
from ..models.team_info import TeamInfo
from ..models.team import AllTeam, OurTeam, OpponentTeam, OpponentLane
from ..models.summoner_info import SummonerInfo
from ..models.summoner import Summoner, create_summoner, get_champion_mastery_by_name
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

api_key = os.environ.get("RIOT_API_KEY_5")

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
async def get_team_info(team_info: TeamInfo, db: Session = Depends(get_db)):
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

    print("Received data:", my_lane, our_team, opponent_team)

    if my_lane != "ALL" and (our_team or opponent_team) and table_check:
        print("!!!!!!!!!!!!!!!!!!!!", table_check)
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

    return {"myLane": my_lane, "ourTeam": our_team, "opponentTeam": opponent_team}


@router.post("/banpick/search")
async def get_summoner_name(summoner_info: SummonerInfo, db: Session = Depends(get_db)):
    print("Received data:", summoner_info)

    db_summoner = Summoner(summonerName=summoner_info.summonerName)
    db_summoner = create_summoner(db, db_summoner)

    champion_mastery = get_champion_mastery_by_name(summoner_info.summonerName, api_key)

    return {
        "summonerName": db_summoner.summonerName,
        "championMastery": champion_mastery,
    }
