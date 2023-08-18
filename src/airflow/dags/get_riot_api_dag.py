from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from utils.request_limiter import RequestLimiter
import time

one_second_limiter = RequestLimiter(max_requests=20, per_seconds=1)
two_minute_limiter = RequestLimiter(max_requests=100, per_seconds=120)


def _wait_for_request():
    while True:
        one_second_limiter.wait_for_request_slot()
        two_minute_limiter.wait_for_request_slot()

        if one_second_limiter.requests < one_second_limiter.max_requests and \
                two_minute_limiter.requests < two_minute_limiter.max_requests:
            break


with DAG(
    dag_id='get_riot_api',
    schedule_interval=None,
    # schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 8, 17),
    catchup=False,
) as dag:

    @task()
    def get_summoners_by_tier(key_num):

        from utils.riot_util import get_summoner_info_by_tier_division_page, get_high_elo_summoner_info
        from utils.common_util import setup_task
        import json

        api_key, redis_conn, logging = setup_task(key_num)

        existing_user = 'processed_summoners_ids'
        processed_summoner_ids = set(member.decode() for member in redis_conn.smembers(existing_user))
        logging.info(f"redis {len(processed_summoner_ids)}")

        days_since_start = (datetime.now() - datetime(2023, 8, 17)).days
        start_page = (days_since_start * 4) % 200
        page = start_page + key_num

        tier_list = ["DIAMOND", "EMERALD", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
        division_list = ["I", "II", "III", "IV"]

        redis_key = f"summoner_data_{key_num}"

        for tier in tier_list:
            for division in division_list:
                try:
                    json_data = get_summoner_info_by_tier_division_page(tier, division, page, api_key)
                    time.sleep(1.2)
                    for data in json_data:
                        summoner_id = data['summonerId']

                        if summoner_id not in processed_summoner_ids:
                            summoner_data = json.dumps({
                                'tier': tier,
                                'division': division,
                                'summoner_id': data['summonerId'],
                                'summoner_name': data['summonerName'],
                            })
                            redis_conn.sadd(redis_key, summoner_data)
                            redis_conn.sadd(existing_user, summoner_id)

                except KeyError:
                    logging.error("api key limit")
                    continue

        # ex) 월요일:0, 화요일: 1, ... 일요일: 6
        current_day_of_week = datetime.today().weekday()
        high_elo_list = ["challenger", "grandmaster", "master"]

        for high_elo in high_elo_list:
            try:
                json_data = get_high_elo_summoner_info(high_elo, api_key)
                time.sleep(1.2)
                json_data_length = len(json_data['entries'])
                today_start_index = (current_day_of_week * json_data_length) // 7

                if current_day_of_week != 6:
                    today_end_index = ((current_day_of_week + 1) * json_data_length) // 7
                else:
                    today_end_index = json_data_length

                segment_length = (today_end_index - today_start_index) // 3

                key_num_start_index = today_start_index + segment_length * key_num
                key_num_end_index = key_num_start_index + segment_length if key_num != 2 else today_end_index

                selected_entries = json_data['entries'][key_num_start_index:key_num_end_index]

                for data in selected_entries:
                    high_elo_summoner_data = json.dumps({
                        'tier': high_elo.upper(),
                        'division': "0",
                        'summoner_id': data['summonerId'],
                        'summoner_name': data['summonerName'],
                    })

                    redis_conn.sadd(redis_key, high_elo_summoner_data)
            except KeyError:
                logging.error("api key limit")
                continue


    @task()
    def get_match_list(key_num):
        import datetime
        from utils.common_util import setup_task
        from utils.riot_util import get_puuid_by_id, get_match_history
        import json

        api_key, redis_conn, logging = setup_task(key_num)

        summoner_part = f"summoner_data_{key_num}"
        summoner_ids = [json.loads(member.decode()) for member in redis_conn.smembers(summoner_part)]
        logging.info(f"redis {len(summoner_ids)}")

        existing_match = 'processed_match_ids'
        processed_match_ids = set(member.decode() for member in redis_conn.smembers(existing_match))
        logging.info(f"redis {len(processed_match_ids)}")

        # 7일 전의 datetime
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        seven_days_ago_timestamp_in_seconds = int(seven_days_ago.timestamp())

        # TODO TIER_MATCH_COUNT 변경
        TIER_MATCH_COUNT = 1000
        tier_list = ["CHALLENGER", "GRANDMASTER", "MASTER", "DIAMOND", "EMERALD", "PLATINUM", "GOLD", "SILVER",
                     "BRONZE", "IRON"]
        division_list = ["I", "II", "III", "IV"]

        match_list_by_tier = {}
        for tier in tier_list:
            if tier in ["CHALLENGER", "GRANDMASTER", "MASTER"]:
                match_list_by_tier[tier] = []
            else:
                for division in division_list:
                    match_list_by_tier[tier + division] = []

        for summoner in summoner_ids:
            tier = summoner['tier']
            if summoner['tier'] not in ["CHALLENGER", "GRANDMASTER", "MASTER"]:
                tier = summoner['tier'] + summoner['division']

            # 현재 티어의 match가 이미 20개를 넘겼다면, 다음 summoner로 넘어감
            if len(match_list_by_tier[tier]) >= TIER_MATCH_COUNT:
                continue

            puuid = get_puuid_by_id(summoner['summoner_id'], api_key)
            summoner['puuid'] = puuid if puuid else None
            if puuid:
                logging.info(f'Success to fetch puuid for {summoner["summoner_name"]} - {summoner["puuid"]}')
            else:
                logging.error(f"Failed to fetch puuid for {summoner['summoner_name']} after retries, puuid set to None")
            _wait_for_request()

            puuid = summoner['puuid']

            # match 중에 중복되는 거 있는지 검사
            matches = get_match_history(puuid, seven_days_ago_timestamp_in_seconds, 1, 100, api_key)
            unique_matches = [match for match in matches if match not in processed_match_ids]

            if unique_matches:
                if len(match_list_by_tier[tier]) + len(matches) > TIER_MATCH_COUNT:
                    needed_matches = TIER_MATCH_COUNT - len(match_list_by_tier[tier])
                    match_list_by_tier[tier].extend(matches[:needed_matches])
                    match_ids_to_add = [match for match in unique_matches[:needed_matches]]
                    processed_match_ids.update([match for match in unique_matches[:needed_matches]])
                    redis_conn.sadd(existing_match, *match_ids_to_add)
                else:
                    match_list_by_tier[tier].extend(matches)
                    match_ids_to_add = [match for match in unique_matches]
                    processed_match_ids.update([match for match in unique_matches])
                    redis_conn.sadd(existing_match, *match_ids_to_add)

            logging.info(f'{tier} : {len(match_list_by_tier[tier])}')
            _wait_for_request()

            if all(len(match_list) >= TIER_MATCH_COUNT for match_list in match_list_by_tier.values()):
                break

        redis_key = f"match_data_{key_num}"
        for tier in match_list_by_tier.keys():
            match_list = match_list_by_tier[tier]
            for match in match_list:
                match_data = json.dumps({
                    'tier': tier,
                    'matchId': match
                })
                redis_conn.sadd(redis_key, match_data)
                logging.info(match_data)


    @task()
    def extract_match_data(key_num):
        from utils.common_util import setup_task
        from utils.riot_util import get_match_details
        from utils.common_util import upload_to_s3
        import pandas as pd
        import json

        api_key, redis_conn, logging = setup_task(key_num)
        redis_key = f'match_data_{key_num}'
        match_data_set = [member.decode() for member in redis_conn.smembers(redis_key)]
        # match_data_set = redis_conn.smembers(redis_key)

        tier_list = []
        match_ids = []
        for match_data in match_data_set:
            match = json.loads(match_data)
            tier_list.append(match['tier'])
            match_ids.append(match['matchId'])

        data = {'tier': [], 'match_id': [], 'team_id': [], 'position': [], 'kills': [], 'deaths': [], 'assists': [],
                'win': [], 'champion_name': [], 'champion_id': [], 'patch': []}
        total_df = pd.DataFrame(data)

        for index, match_id in enumerate(match_ids):
            # todo  sql matchId로 puuId 찾고, summoner Table에서 puuId 조건 걸면 하나의 행이 나온다.
            match_details = get_match_details(match_id, api_key)
            try:
                team_id = [participant['teamId'] for participant in match_details['info']['participants']]
                position = [participant['teamPosition'] for participant in match_details['info']['participants']]
                kills = [participant['kills'] for participant in match_details['info']['participants']]
                deaths = [participant['deaths'] for participant in match_details['info']['participants']]
                assists = [participant['assists'] for participant in match_details['info']['participants']]
                win = [participant['win'] for participant in match_details['info']['participants']]
                champion_name = [participant['championName'] for participant in match_details['info']['participants']]
                champion_id = [participant['championId'] for participant in match_details['info']['participants']]
                patch = (match_details['info']['gameVersion'])[:5]

                data = {'tier': [], 'match_id': [], 'team_id': [], 'position': [], 'kills': [], 'deaths': [],
                        'assists': [], 'win': [], 'champion_name': [], 'champion_id': [], 'patch': []}
                if len(team_id) == 10:
                    for i in range(10):
                        data['tier'].append(tier_list[index])
                        data['match_id'].append(match_id)
                        data['team_id'].append(team_id[i])
                        data['position'].append(position[i])
                        data['kills'].append(kills[i])
                        data['deaths'].append(deaths[i])
                        data['assists'].append(assists[i])
                        data['win'].append(win[i])
                        data['champion_name'].append(champion_name[i])
                        data['champion_id'].append(champion_id[i])
                        data['patch'].append(patch)

                    df = pd.DataFrame(data)
                    total_df = pd.concat([total_df, df], ignore_index=True)
            except KeyError:
                logging.info("!!")
                logging.info(match_details['status'])
            time.sleep(1.2)

        upload_to_s3(total_df, 'match', key_num)

    @task()
    def get_champion_mastery(key_num):
        from utils.common_util import setup_task
        from utils.riot_util import get_champion_mastery_by_id
        from utils.common_util import upload_to_s3
        import pandas as pd
        import os
        import json

        api_key, redis_conn, logging = setup_task(key_num)
        redis_key = f"summoner_data_{key_num}"
        summoner_ids = [json.loads(member.decode()) for member in redis_conn.smembers(redis_key)]

        id_list = []
        for summoner in summoner_ids:
            id_list.append(summoner['summoner_id'])
        script_path = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(script_path, 'utils', 'champion_dictionary.json')
        with open(json_file_path, 'r') as json_file:
            json_data = json_file.read()

        champion_dict = json.loads(json_data)
        data = {'id': []}
        data.update({key: [] for key in champion_dict.keys() if key != 'id'})
        total_df = pd.DataFrame(data)
        logging.info(len(id_list))
        for id in id_list:
            tmp = get_champion_mastery_by_id(id, api_key)
            champion_id = []
            champion_points = []
            for champion in tmp:
                champion_id.append(champion['championId'])
                champion_points.append(champion['championPoints'])
            data = {'id': []}
            data.update({key: [] for key in champion_dict.keys() if key != 'id'})

            data['id'].append(id)

            for i in range(len(champion_id)):
                if str(champion_id[i]) in data:
                    data[str(champion_id[i])].append(champion_points[i])

            for key in data.keys():
                if key != 'id' and not data[key]:
                    data[key].append(0)

            df = pd.DataFrame(data)
            total_df = pd.concat([total_df, df], ignore_index=True)
            time.sleep(1.2)

        upload_to_s3(total_df, 'mastery', key_num)


    @task()
    def delete_redis_key():
        from utils.common_util import setup_task
        api_key, redis_conn, logging = setup_task(1)
        for key in range(3):
            summoner_data_key = f"summoner_data_{key}"
            match_data_key = f"match_data_{key}"

            redis_conn.delete(summoner_data_key)
            redis_conn.delete(match_data_key)


    start = EmptyOperator(task_id='start')

    with TaskGroup(group_id='sumoners_task_group') as summoners_task_group:
        summoners_task_1 = get_summoners_by_tier(1)
        summoners_task_2 = get_summoners_by_tier(2)
        summoners_task_3 = get_summoners_by_tier(3)

    with TaskGroup(group_id='match_list_task_group') as match_list_task_group:
        match_list_task_1 = get_match_list(1)
        match_list_task_2 = get_match_list(2)
        match_list_task_3 = get_match_list(3)

    with TaskGroup(group_id='match_task_group') as match_task_group:
        match_task_1 = extract_match_data(1)
        match_task_2 = extract_match_data(2)
        match_task_3 = extract_match_data(3)

    with TaskGroup(group_id='mastery_task_group') as mastery_task_group:
        mastery_task_1 = get_champion_mastery(1)
        # mastery_task_2 = get_champion_mastery(2)
        # mastery_task_3 = get_champion_mastery(3)

    delete_redis_key_task = delete_redis_key()

    end = EmptyOperator(task_id='end')

    start >> summoners_task_group >> match_list_task_group >> match_task_group
    match_task_group >> mastery_task_group >> delete_redis_key_task >> end
