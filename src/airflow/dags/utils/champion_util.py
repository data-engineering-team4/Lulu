import json

def champion_info_extraction():
    """
    1. 챔피언 업데이트때마다  https://developer.riotgames.com/docs/lol champion.json 검색해서 다운 후 champion.json 업데이트
    2. champion_info_extraction 실행하면 champion_dictionary.json이 업데이트 됨
    3. 신챔프 추가시 champion_mapping_ko_en.json을 수작업으로 추가 해줘야 한다.
    """
    with open("champion.json", "r") as file:
        json_data = file.read()

    data = json.loads(json_data)
    champion_dict = {champion["key"]: champion["name"] for champion in data["data"].values()}

    with open("champion_dictionary.json", "w") as file:
        json.dump(champion_dict, file)