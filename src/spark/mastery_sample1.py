import boto3
import pandas as pd
import os
from dotenv import load_dotenv
from io import BytesIO
import json

load_dotenv()

aws_access_key_id = os.environ.get("aws_access_key_id")  # 테스트용 파이썬 파일이라 env 파일 이용
aws_secret_access_key = os.environ.get("aws_secret_access_key")
bucket_name = "de-4-2"
file_key = "data/mastery/2023-08-20/data1.csv"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
content = response["Body"].read()

csv_data = BytesIO(content)
csv_df = pd.read_csv(csv_data, encoding="utf-8", usecols=lambda column: column != "id")

directory = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(directory, "../airflow/dags/utils/champion_dictionary.json")

with open(json_file_path, "r", encoding="utf-8") as json_file:
    champion_dict = json.load(json_file)

columns = list(champion_dict.values())
csv_df.rename(
    columns={
        old_column: new_column
        for old_column, new_column in zip(csv_df.columns, columns)
    },
    inplace=True,
)


from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

num_champions = 10

json_file_path = os.path.join(directory, "../airflow/dags/utils/champion_mapping_ko_en.json")
with open(json_file_path, "r", encoding="utf-8") as f:
    champion_mapping_ko_en = json.load(f)
champion_mapping_en_kr = {value: key for key, value in champion_mapping_ko_en.items()}

scaler = StandardScaler()
df = pd.DataFrame(scaler.fit_transform(csv_df), columns=csv_df.columns)

df_transposed = df.transpose()

cosine_sim = cosine_similarity(df_transposed)  # 코사인말고도 계산법은 많지만 여기서 더 유의미한 결과값은 안 나올 듯
cosine_sim_df = pd.DataFrame(cosine_sim, index=df.columns, columns=df.columns)

champion = champion_mapping_ko_en["이렐리아"]
similar_champions = cosine_sim_df[champion].sort_values(ascending=False)[
    1 : num_champions + 1
]
print(similar_champions)
similar_champions = similar_champions.index.map(champion_mapping_en_kr).tolist()

print(similar_champions)

# 이건 학습 개념이 없어서 나중에 데이터를 축적하고 한 번씩 돌리는 게 베스트인 듯
# 여기서 더 손본다면 dag형식으로 바꾸고 주기를 설정해서 해당 주기의 데이터를 전부 가져오게 하는 기능 추가해야 할 듯?
