from pymongo import MongoClient

client = MongoClient("REMOVED_MONGODB_URI")
db = client["darkweb"]
collection = db["leaked_data"]

result = collection.delete_many({"_id": {"$regex": "^gunra_"}})
print(f"{result.deleted_count}개의 문서 삭제 완료 ✅")