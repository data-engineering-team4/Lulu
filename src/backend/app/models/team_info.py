from pydantic import BaseModel
from typing import Dict
import json


class TeamInfo(BaseModel):
    ourTeam: Dict[int, int]
    opponentTeam: Dict[int, int]
    myLane: int

    def to_json(self):
        return json.dumps(self.dict())
