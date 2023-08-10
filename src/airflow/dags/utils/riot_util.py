import requests
from datetime import datetime, timedelta

def get_request_headers(api_key):
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ko-KR;q=0.8,ko;q=0.7",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": api_key
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

def get_match_history(puu_id, num_match, api_key):
    """
    puu_id를 기준으로 matchid list를 반환.
    """
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puu_id}/ids?count={num_match}"
    return get_json_response(url, api_key)

def get_match_details(match_id, api_key):
    """
    match_id로 해당 match의 정보를 반환.
    """
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
    return get_json_response(url, api_key)

def convert_to_kst(timestamp_ms):
    """
    unix timestamp를 한국시간대(kst)로 변환.
    """
    timestamp_s = timestamp_ms / 1000
    datetime_utc = datetime.utcfromtimestamp(timestamp_s)
    datetime_kst = datetime_utc + timedelta(hours=9)

    return datetime_kst

def get_puuid_by_name(summoner_name, api_key):
    """
    summoner_name으로 puuid 반환.
    """
    summoner_details = get_summoner_details(summoner_name, api_key)
    puu_id = summoner_details['puuid']
    return puu_id

def get_champion_mastery_by_name(summoner_name, api_key):
    """
    summoner_name으로 챔피언 숙련도 반환.
    """
    puu_id = get_puuid_by_name(summoner_name, api_key)
    url = f"https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puu_id}"
    return get_json_response(url, api_key)

def get_champion_mastery_by_puuid(puu_id, api_key):
    """
    puu_id로 챔피언 숙련도 반환.
    """
    url = f"https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puu_id}"
    return get_json_response(url, api_key)

def get_summoner_info_by_tier_division_page(tier, division, page, api_key):
    """
    tier로 summoner 정보 반환.
    """
    url = f"https://kr.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/{tier}/{division}?page={page}"
    return get_json_response(url, api_key)

def get_high_elo_summoner_info(high_elo, api_key):
    """
    천상계 summoner 정보 반환.
    """
    url = f"https://kr.api.riotgames.com/lol/league/v4/{high_elo}leagues/by-queue/RANKED_SOLO_5x5"
    return get_json_response(url, api_key)