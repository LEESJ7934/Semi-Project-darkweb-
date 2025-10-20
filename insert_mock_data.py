from pymongo import MongoClient
from datetime import datetime
import sys

# --- 1. 설정 (test_db.py와 동일) ---
MONGO_CONN_STR = "mongodb://localhost:27017/"
DB_NAME = "ransomware_db"  # 1번 팀원과 동일
COLLECTION_NAME = "victims"  # 1번 팀원과 동일

# --- 2. '진짜 같은' 가짜 데이터 정의 ---

# Case 1: 'DIRECT' (알림 와야 함)
# 1번 팀원의 crawling_test.py 구조를 참고
mock_data_direct = {
    "victim_name": "My Fake Corp (DIRECT)",
    "victim_domain": "myfake.co.kr",
    "source_url": "http://dark.web/myfake_corp",
    "ransomware_group": "TestGroup",
    "description_text": "We are TestGroup. We hacked myfake.co.kr",
    "is_korea_related": True,
    "korea_mention_type": "DIRECT",  # PDF 로직
    "detected_keywords_direct": ".co.kr",
    "detected_keywords_indirect": None,
    "created_at": datetime.now(),
}

# Case 2: 'MENTION' (알림 오면 안 됨)
mock_data_mention = {
    "victim_name": "USA Company (MENTION)",
    "victim_domain": "usa-company.com",
    "source_url": "http://dark.web/usa-company",
    "ransomware_group": "TestGroup",
    "description_text": "Our partner is Samsung in Korea.",
    "is_korea_related": True,
    "korea_mention_type": "MENTION",  # PDF 로직
    "detected_keywords_direct": None,
    "detected_keywords_indirect": "Samsung",
    "created_at": datetime.now(),
}


def setup_database():
    client = None
    try:
        client = MongoClient(MONGO_CONN_STR)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # (테스트를 위해 기존 가짜 데이터 모두 삭제)
        collection.delete_many({})
        print(">>> 기존 'victims' 컬렉션의 데이터를 모두 삭제했습니다.")

        # Case 1 삽입
        result_direct = collection.insert_one(mock_data_direct)
        print(f"--- 'DIRECT' 데이터 삽입 성공 ---")
        print(f"ID: {result_direct.inserted_id}")

        # Case 2 삽입
        result_mention = collection.insert_one(mock_data_mention)
        print(f"--- 'MENTION' 데이터 삽입 성공 ---")
        print(f"ID: {result_mention.inserted_id}")

        print("\n>>> MongoDB Compass로 'ransomware_db.victims'를 확인해보세요.")
        print(">>> 이제 이 ID들을 복사해서 'alerter.py'를 테스트할 수 있습니다.")

    except Exception as e:
        print(f">>> DB 설정 실패: {e}")
    finally:
        if client:
            client.close()


if __name__ == "__main__":
    if not hasattr(sys, "prefix") or sys.prefix == sys.base_prefix:
        print(
            "경고: 가상환경(.venv)이 활성화되지 않았습니다. 활성화 후 다시 실행하세요."
        )
    else:
        setup_database()
