import json
import os


def champion_info_extraction():
    """
    1. 챔피언 업데이트때마다  https://developer.riotgames.com/docs/lol champion.json 검색해서 다운 후 champion.json 업데이트
    2. champion_info_extraction 실행하면 champion_dictionary.json이 업데이트 됨
    3. 신챔프 추가시 champion_mapping_ko_en.json을 수작업으로 추가 해줘야 한다.
    """
    current_directory = os.path.dirname(os.path.abspath(__file__))
    champion_path = os.path.join(current_directory, "champion.json")
    champion_dict_path = os.path.join(current_directory, "champion_dictionary.json")

    with open(champion_path, "r", encoding="utf-8") as file:
        json_data = file.read()

    data = json.loads(json_data)
    champion_dict = {
        champion["key"]: champion["name"] for champion in data["data"].values()
    }
    print(len(champion_dict))

    with open(champion_dict_path, "w") as file:
        json.dump(champion_dict, file)
