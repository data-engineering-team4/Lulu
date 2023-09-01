from fastapi import APIRouter, Depends
from ..models.team_info import TeamInfo
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
print(kinesis_stream_name)
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

api_key = os.environ.get("RIOT_API_KEY_5")

client = boto3.client(
    "kinesis",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name="ap-northeast-3",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/banpick/produce")
async def get_team_info(team_info: TeamInfo):
    print("Received data:", team_info)
    response = client.put_record(
        StreamName=kinesis_stream_name, Data="my_data", PartitionKey="partition_key"
    )

    return {"ourTeam": team_info.ourTeam, "opponentTeam": team_info.opponentTeam}

@router.post("/banpick/search")
async def get_summoner_name(summoner_info: SummonerInfo, db: Session = Depends(get_db)):
    print("Received data:", summoner_info)

    db_summoner = Summoner(summonerName=summoner_info.summonerName)
    db_summoner = create_summoner(db, db_summoner)

    champion_mastery = get_champion_mastery_by_name(summoner_info.summonerName, api_key)
    
    return {"summonerName": db_summoner.summonerName, "championMastery": champion_mastery}
