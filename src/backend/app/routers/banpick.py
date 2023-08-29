from fastapi import APIRouter, Depends
from ..models.team_info import TeamInfo
from ..models.summoner_info import SummonerInfo
from ..models.summoner import Summoner, create_summoner
from ..db_session import SessionLocal
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import json
from kinesis.producer import KinesisProducer

router = APIRouter()
load_dotenv()

kinesis_stream_name = os.environ.get("KINESIS_STREAM_NAME")
kinesis_producer = KinesisProducer(
    stream_name=kinesis_stream_name
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
    kinesis_producer.put_record(
        json.dumps(team_info.dict())
    )

    return {"ourTeam": team_info.ourTeam, "opponentTeam": team_info.opponentTeam}


@router.post("/banpick/search")
async def get_summoner_name(summoner_info: SummonerInfo, db: Session = Depends(get_db)):
    print("Received data:", summoner_info)
    db_summoner = Summoner(summonerName=summoner_info.summonerName)
    db_summoner = create_summoner(db, db_summoner)
    return {"summonerName": db_summoner.summonerName}
