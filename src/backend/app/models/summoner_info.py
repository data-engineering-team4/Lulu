from pydantic import BaseModel


class SummonerInfo(BaseModel):
    summonerName: str
