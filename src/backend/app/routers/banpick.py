from fastapi import APIRouter, Depends
from ..models.team_info import TeamInfo
from ..models.summoner_info import SummonerInfo
from ..models.summoner import Summoner, create_summoner
from confluent_kafka import Producer
from ..db_session import SessionLocal
from sqlalchemy.orm import Session
import os

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
p = Producer({"bootstrap.servers": bootstrap_servers})


@router.post("/banpick/produce")
async def get_team_info(team_info: TeamInfo):
    print("Received data:", team_info)
    p.produce("testfastapi", value=str(team_info.dict()))
    p.flush()

    return {"ourTeam": team_info.ourTeam, "opponentTeam": team_info.opponentTeam}


@router.post("/banpick/search")
async def get_summoner_name(summoner_info: SummonerInfo, db: Session = Depends(get_db)):
    print("Received data:", summoner_info)
    db_summoner = Summoner(summonerName=summoner_info.summonerName)
    db_summoner = create_summoner(db, db_summoner)
    return {"summonerName": db_summoner.summonerName}
