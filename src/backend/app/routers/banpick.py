from fastapi import APIRouter
from ..models.team_info import TeamInfo
from ..models.summoner_info import SummonerInfo
import os
from confluent_kafka import Producer

router = APIRouter()

# todo fastapi는 비동기 프레임워크, ThreadPoolExecutor 등을 사용하여 프로듀서와 컨슈머를 비동기로 처리하면
# I/O 바운드 작업이나 HTTP 요청 처리하는 등 다른 비동기 작업을 동시에 수행하여 다수의 클라이언트와 동시에 통신할 때 효율적

develop_server_address = ""
bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", develop_server_address)
p = Producer({"bootstrap.servers": bootstrap_servers})


@router.post("/banpick/produce")
async def get_team_info(team_info: TeamInfo):
    print("Received data:", team_info)
    p.produce("testfastapi", value=str(team_info.dict()))
    p.flush()

    return {"ourTeam": team_info.ourTeam, "opponentTeam": team_info.opponentTeam}


@router.post("/banpick/search")
async def get_summoner_name(summoner_info: SummonerInfo):
    print("Received data:", summoner_info)
    # 숙련도 처리 로직
    return {"summonerName": summoner_info.summonerName}
