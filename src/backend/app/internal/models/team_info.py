from pydantic import BaseModel
from typing import Dict


class TeamInfo(BaseModel):
    ourTeam: Dict[int, int]
    opponentTeam: Dict[int, int]