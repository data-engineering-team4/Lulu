import boto3
import pandas as pd
import os
from dotenv import load_dotenv
from io import BytesIO
import json

load_dotenv()

aws_access_key_id = os.environ.get("aws_access_key_id")
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
csv_df = pd.read_csv(csv_data, encoding="utf-8")

directory = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(directory, "utils/champion_mapping_ko_en.json")

with open(json_file_path, "r", encoding="utf-8") as json_file:
    champion_mapping_ko_en = json.load(json_file)

columns = list(champion_mapping_ko_en.keys())
columns.insert(0, "id")


from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("KMeansExample").getOrCreate()

df = spark.createDataFrame(csv_df, columns)

assembler = VectorAssembler(inputCols=columns[1:], outputCol="features")
df_assembled = assembler.transform(df)

kmeans = KMeans(k=3, seed=1)  # 군집을 몇 개 생성하냐 -> k는 높일수록 더 많은 군집, 기능에 따라 높이거나 낮출 듯
model = kmeans.fit(
    df_assembled
)  # seed값(클러스터 초기 중심점)은 결과에 크게 영향을 미치지는 않지만 최적의 값을 찾으면 안정성을 높일 수 있음

input_attributes = [
    "123",
    0,
    11958,
    13543,
    0,
    79759,
    10624,
    7134,
    4092,
    10275,
    133175,
    128,
    20165,
    4217,
    0,
    55480,
    0,
    161,
    176713,
    26961,
    14573,
    5242,
    13736,
    1524,
    238,
    0,
    3860,
    56256,
    12615,
    10029,
    754578,
    1191,
    42550,
    1709,
    14124,
    0,
    4799,
    26329,
    3484,
    35814,
    0,
    1131,
    165,
    504,
    33680,
    0,
    4830,
    1468,
    13649,
    7717,
    204589,
    55020,
    213717,
    56854,
    0,
    2025,
    11804,
    9400,
    2763,
    16733,
    7822,
    5773,
    38390,
    6472,
    51488,
    0,
    30540,
    160044,
    41459,
    417,
    422,
    262561,
    160,
    33773,
    11438,
    6661,
    92,
    0,
    0,
    5921,
    0,
    0,
    63711,
    0,
    0,
    1947,
    6101,
    0,
    8522,
    0,
    1403,
    521,
    0,
    16585,
    3742,
    2854,
    9139,
    31772,
    929,
    7218,
    4437,
    1508,
    12277,
    0,
    0,
    0,
    1123,
    23454,
    5980,
    8434,
    36546,
    1293,
    9504,
    147,
    0,
    5544,
    4389,
    1500,
    697,
    1327,
    72826,
    3367,
    0,
    3517,
    9007,
    7800,
    4187,
    1349,
    497,
    4333,
    0,
    5294,
    78635,
    108271,
    159,
    3230,
    10871,
    21991,
    2645,
    1031,
    161937,
    390288,
    3615,
    2250,
    0,
    0,
    6250,
    41872,
    23826,
    5744,
    4676,
    207503,
    11806,
    847,
    65211,
    4246,
    0,
    23638,
    3444,
    10780,
    0,
    884,
    465,
    29780,
    0,
]  # 이건 특정 유저의 아이디 및 숙련도(데이터셋으로 사용한 유저들 중 한 유저의 아이디와 숙련도를 조금 바꿔도 기가막히게 찾아주긴 함)

input_df = spark.createDataFrame([input_attributes], columns)

input_assembled = assembler.transform(input_df)

input_cluster = (
    model.transform(input_assembled).select("prediction").first().prediction
)  # 찾은 클러스터(유저 군집) 중 첫 번째
cluster_data = model.transform(df_assembled).filter(
    col("prediction") == input_cluster
)  # 위의 옵션으로 찾아줘라
first_column_value = cluster_data.select(columns[0]).first()[
    0
]  # 찾은 컬럼 중 첫 번째 값만 반환, 예시로 유저 아이디만 가져오게 함(나중에 유저 이름같은 걸로 바꿔도?)

print("가장 비슷한 클러스터의 첫 번째 유저 아이디 값:", first_column_value)

spark.stop()

# 지금은 mastery 자료에 유저 이름이 없는데 나중에 비슷한 프로게이머를 추천해주는 기능을 넣는다면
# 그 때는 유저 네임을 추가하여 이름을 추천하고 클릭하면 그 추천 유저의 숙련도 페이지로 넘어가는 기능도 괜찮을 듯
