from pymongo import MongoClient
from datetime import datetime
import sys

# --- 1. 설정 ---
# 3.1단계에서 설치한 '가짜 DB' 접속 정보
MONGO_CONN_STR = "mongodb://localhost:27017/"
DB_NAME = "ransomware_db"  # 1번 팀원 코드(crawling.py)와 동일
COLLECTION_NAME = "victims"  # 1번 팀원 코드(crawling.py)와 동일

# 1번 팀원이 crawling_test.py에서 사용할 가짜 데이터 구조
mock_data = {
    "victim_name": "Test Corp for DB",
    "victim_domain": "test.com",
    "korea_mention_type": "DIRECT",
    "created_at": datetime.now(),
}


def test_db_connection():
    """
    MongoDB에 연결하여 데이터 1개를 삽입(Create)하고
    즉시 다시 조회(Read)하여 연결을 테스트합니다.
    """
    client = None
    try:
        # --- 2. DB 연결 ---
        # 'pymongo'(통역사)를 통해 DB 서버에 연결
        client = MongoClient(MONGO_CONN_STR)

        # 'ransomware_db'라는 DB를 선택
        db = client[DB_NAME]
        # 그 안의 'victims'라는 컬렉션(테이블)을 선택
        collection = db[COLLECTION_NAME]

        print(">>> MongoDB 서버에 성공적으로 연결되었습니다.")

        # --- 3. 데이터 1개 넣기 (Create) ---
        # collection.insert_one() 함수로 'mock_data'를 DB에 삽입
        result = collection.insert_one(mock_data)
        inserted_id = result.inserted_id

        print(f">>> 데이터 1개 삽입 성공. ID: {inserted_id}")

        # --- 4. 데이터 1개 읽기 (Read) ---
        # 방금 넣은 ID를 기준으로 데이터 1개를 다시 조회
        found_data = collection.find_one({"_id": inserted_id})

        if found_data:
            print(">>> 방금 삽입한 데이터 조회 성공:")
            print(found_data)
        else:
            print(">>> !!! 오류: 삽입한 데이터를 찾을 수 없습니다.")

    except Exception as e:
        print(f">>> DB 연결 또는 테스트 실패: {e}")
        print(">>> 1. MongoDB 서버(Docker)가 실행 중인지 확인하세요.")
        print(">>> 2. MongoDB Compass로 localhost:27017 연결이 되는지 확인하세요.")
    finally:
        # DB 연결은 항상 닫아주어야 함
        if client:
            client.close()
            print(">>> MongoDB 연결을 닫았습니다.")


# --- 스크립트 실행 ---
if __name__ == "__main__":
    # (.venv) 환경에서 실행해야 함
    if not hasattr(sys, "prefix") or sys.prefix == sys.base_prefix:
        print("=" * 50)
        print("경고: 가상환경(.venv)이 활성화되지 않은 것 같습니다.")
        print("터미널에서 `S:\\jeong\\DarkWeb\\.venv\\Scripts\\Activate.ps1` 실행 후")
        print("다시 `python test_db.py`를 실행하세요.")
        print("=" * 50)

    test_db_connection()
