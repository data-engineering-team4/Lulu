from fastapi import APIRouter
from models.team_info import TeamInfo
from models.summoner_info import SummonerInfo

router = APIRouter()


@router.post("/banpick/produce")
async def get_team_info(team_info: TeamInfo):
    print("Received data:", team_info)
    # 카프카로 보내는 로직
    return {"ourTeam": team_info.ourTeam, "opponentTeam": team_info.opponentTeam}


@router.post("/banpick/search")
async def get_summoner_name(summoner_info: SummonerInfo):
    print("Received data:", summoner_info)
    # 숙련도 처리 로직
    return {"summonerName": summoner_info.summonerName}
