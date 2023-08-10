from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)
# env_path = os.path.join(os.path.dirname(__file__), '../../../.env')
# load_dotenv(dotenv_path=env_path)
# api_key = os.getenv("API_KEY")

with DAG(
    dag_id = 'get_summoners_by_tier',
    schedule_interval=None,
    # schedule_interval=timedelta(days=1),
    start_date = datetime(2023,8,8),
    catchup=False,
) as dag:

    @task()
    def get_summoners_by_tier():

        from utils.riot_util import get_summoner_info_by_tier_division_page
        import time

        api_key = ""
        tier_list = ["DIAMOND", "EMERALD", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
        division_list = ["I", "II", "III", "IV"]

        summoner_data_list = []
        days_since_start = (datetime.now() - datetime(2023, 8, 10)).days
        start_page = (days_since_start * 4) % 200 + 1
        end_page = start_page + 3

        for tier in tier_list:
            for division in division_list:
                for page in range(start_page, end_page + 1):
                    # logging.info(f"Processing tier {tier}, division {division}, page {page}")
                    json_data = get_summoner_info_by_tier_division_page(tier, division, page, api_key)
                    logging.info(json_data)
                    for data in json_data:
                        logging.info(data)
                        summoner_data_list.append({
                            'tier': tier,
                            'division': division,
                            'summoner_id': data['summonerId'],
                            'summoner_name': data['summonerName'],
                        })
                    time.sleep(1.2)

        return summoner_data_list

    get_summoners_by_tier()