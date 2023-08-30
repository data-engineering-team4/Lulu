# Tiers and divisions
TIERS = ["DIAMOND", "EMERALD", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
DIVISIONS = ["I", "II", "III", "IV"]

# High ELO tiers
HIGH_ELO_LIST = ["CHALLENGER", "GRANDMASTER", "MASTER"]

# Match counts for tiers (최적화값=1000)
TIER_MATCH_COUNT = 1000

# S3 업로드 임계값
S3_UPLOAD_THRESHOLD = 1000

# 경기 데이터 임계값(최대값=100)
MATCH_THRESHOLD = 100

# S3 Bucket
RAW_MATCH_BUCKET = "raw_match"
RAW_MASTERY_BUCKET = "raw_mastery"

TRANSFORMED_MATCH_BUCKET = "match"
TRANSFORMED_MASTERY_BUCKET = "mastery"
