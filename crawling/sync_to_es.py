# 데이터 동기화 코드

from elasticsearch.helpers import BulkIndexError
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from pymongo import MongoClient

from dotenv import load_dotenv
import os, datetime

load_dotenv()
MONGO_URI = os.getenv("ATLAS_URI")
DB_NAME   = os.getenv("DB_NAME", "darkweb")
ES_URI    = os.getenv("ES_URI", "http://127.0.0.1:9200")
INDEX     = os.getenv("ES_INDEX", "leaked_data")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

es = Elasticsearch(ES_URI)

def gen_actions():
    for doc in db["leaked_data"].find():
        es_id = str(doc.pop("_id"))        
        st = doc.get("scraped_time")
        if isinstance(st, datetime.datetime):
            doc["scraped_time"] = st.isoformat()
        yield {
            "_op_type": "index",
            "_index": INDEX,
            "_id": es_id,
            "_source": doc
        }

try:
    result = bulk(es, gen_actions(), refresh="wait_for")
    print("갱신 완료!")
    print("Result:", result)
except BulkIndexError as e:
    print(" 일부 문서 인덱싱 실패!")
    print(f"총 실패 문서 수: {len(e.errors)}\n")
    
    for i, err in enumerate(e.errors[:3]):
        print(f"[{i+1}] ===============================")
        print(err)