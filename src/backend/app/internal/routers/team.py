from fastapi import APIRouter
from ..models.team_info import TeamInfo

router = APIRouter()


@router.post("/banpick/")
async def read_item(team_info: TeamInfo):
    print("Received data:", team_info)
    return {"ourTeam": team_info.ourTeam, "opponentTeam": team_info.opponentTeam}
