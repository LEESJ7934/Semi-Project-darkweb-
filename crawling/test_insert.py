# crawling/test_insert.py
from datetime import datetime
from crawling.db import db

sample_data = {
    "vendor": "test_forum",
    "url": "http://darkweb.test/post/123",
    "content": "This is a test insert from VSCode!",
    "fetched_at": datetime.utcnow()
}

result = db.raw_docs.insert_one(sample_data)
print("✅ 데이터 저장 성공! _id =", result.inserted_id)