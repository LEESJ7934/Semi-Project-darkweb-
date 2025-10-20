# sync_to_es.py
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from pymongo import MongoClient
from dotenv import load_dotenv
import os, datetime

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME   = os.getenv("DB_NAME", "darkweb")
ES_URI    = os.getenv("ES_URI", "http://127.0.0.1:9200")
INDEX     = os.getenv("ES_INDEX", "leaked_data")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

es = Elasticsearch(ES_URI)

# (선택) 매핑 세팅
if not es.indices.exists(index=INDEX):
    es.indices.create(
        index=INDEX,
        mappings={
            "properties": {
                "company_name": {"type": "text"},
                "company_url":  {"type": "keyword"},
                "description":  {"type": "text"},
                "publication_date": {"type": "date", "format": "yyyy-MM-dd||yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis"},
                "scraped_time": {"type": "date", "format": "strict_date_optional_time||epoch_millis"},
                "source": {"type": "keyword"}
            }
        },
    )

def gen_actions():
    for doc in db["leaked_data"].find():
        es_id = str(doc.pop("_id"))         # <-- ES에서는 _id를 본문에서 제거하고 _id 파라미터로
        st = doc.get("scraped_time")
        if isinstance(st, datetime.datetime):
            doc["scraped_time"] = st.isoformat()
        yield {
            "_op_type": "index",
            "_index": INDEX,
            "_id": es_id,
            "_source": doc
        }

bulk(es, gen_actions(), refresh="wait_for")
print("Synced Mongo → ES")