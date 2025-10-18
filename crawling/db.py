from pymongo import MongoClient
from dotenv import load_dotenv
import os

# .env 파일 불러오기
load_dotenv()

# 환경변수 읽기
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# MongoDB 연결
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print("✅ MongoDB 연결 성공:", db.name)

# 테스트 데이터 삽입
test_doc = {"message": "VSCode에서 MongoDB 연결 테스트 완료!"}
result = db.test_collection.insert_one(test_doc)
print("✅ 데이터 저장 성공! _id =", result.inserted_id)