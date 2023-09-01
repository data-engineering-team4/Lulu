from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from ..db_session import Base
import requests


class Summoner(Base):
    __tablename__ = "summoners"

    id = Column(Integer, primary_key=True, index=True)
    summonerName = Column(String, index=True)


def create_summoner(db: Session, summoner: Summoner):
    db.add(summoner)
    db.commit()
    db.refresh(summoner)
    return summoner


def get_request_headers(api_key):
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ko-KR;q=0.8,ko;q=0.7",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": api_key,
    }


def get_json_response(url, api_key):
    """
    http 요청을 보내고 응답을 json으로 파싱.
    """
    headers = get_request_headers(api_key)
    response = requests.get(url, headers=headers)
    return response.json()


def get_summoner_details(summoner_name, api_key):
    """
    name을 기준으로 summoner를 찾아 정보를 반환.
    """
    url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    return get_json_response(url, api_key)


def get_id_by_name(summoner_name, api_key):
    """
    summoner_name으로 id 반환.
    """
    summoner_details = get_summoner_details(summoner_name, api_key)
    print(summoner_details)
    if "id" in summoner_details:
        id = summoner_details["id"]
        return id


def get_champion_mastery_by_name(summoner_name, api_key):
    """
    summoner_name으로 챔피언 숙련도 반환.
    """
    id = get_id_by_name(summoner_name, api_key)
    url = f"https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{id}"
    return get_json_response(url, api_key)
