import sys
import asyncio
import telegram
from pymongo import MongoClient
from bson.objectid import ObjectId  # (아주 중요!) MongoDB의 'ObjectId'를 다루기 위함
import config  # (새로 추가!) config.py 파일을 가져옵니다.

# -----------------------------------
# 1. 설정 (config.py에서 불러오기)
# -----------------------------------
TELEGRAM_TOKEN = config.TELEGRAM_TOKEN
TELEGRAM_CHAT_ID = config.TELEGRAM_CHAT_ID
MONGO_CONN_STR = config.MONGO_CONN_STR
DB_NAME = config.DB_NAME
COLLECTION_NAME = config.COLLECTION_NAME

# -----------------------------------
# 1. 설정 (2단계, 3단계에서 확인한 값)
# -----------------------------------
# 2단계에서 발급받은 텔레그램 토큰
TELEGRAM_TOKEN = ""
# 2단계에서 확인한 그룹 채팅방 ID
TELEGRAM_CHAT_ID = -  # 여기에 Chat ID (숫자)를 넣으세요

# 3단계에서 설치한 '가짜' MongoDB 접속 정보
MONGO_CONN_STR = "mongodb://localhost:27017/"
DB_NAME = "ransomware_db"  # 1번 팀원 코드(crawling.py)와 동일
COLLECTION_NAME = "victims"  # 1번 팀원 코드(crawling.py)와 동일


# -----------------------------------
# 2. 알림 발송 핵심 함수
# -----------------------------------
async def send_alert_for_id(victim_id_str: str):
    """
    ID(문자열)를 받아 MongoDB에서 조회 후,
    'DIRECT' 등급이면 텔레그램 알림을 보냅니다.
    """
    client = None
    try:
        # --- (3단계 기술) DB 연결 및 데이터 조회 ---
        client = MongoClient(MONGO_CONN_STR)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        print(f"DB에서 ID '{victim_id_str}' 조회 시도...")

        # (핵심!) 1번 팀원이 넘겨줄 ID는 '문자열'입니다.
        # MongoDB에서 조회하려면 'ObjectId' 타입으로 변환해야 합니다.
        victim_object_id = ObjectId(victim_id_str)
        alert_data = collection.find_one({"_id": victim_object_id})

        if not alert_data:
            print(f"데이터 {victim_id_str}를 찾을 수 없음.")
            return

        print(f"데이터 찾음: {alert_data.get('victim_name')}")

        # --- (PDF 로직) 알림 등급 판단 ---
        # is_korea_related: true 인 것 중 korea_mention_type을 확인합니다.
        if alert_data.get("korea_mention_type") == "DIRECT":  #
            print("DIRECT 타입 확인. 알림 구성 시작...")

            # --- (PDF 양식) 메시지 포매팅 ---
            victim_target = alert_data.get("victim_name", "N/A")
            victim_domain = alert_data.get("victim_domain")
            if victim_domain:
                victim_target += f" ({victim_domain})"

            message = (
                f"[🚨 K-MONITOR 위협 속보: 한국 직접 타겟 의심 🚨]\n"
                f"■ 그룹: {alert_data.get('ransomware_group', 'N/A')}\n"
                f"■ 대상: {victim_target}\n"
                f"■ 탐지 키워드: {alert_data.get('detected_keywords_direct', 'N/A')}\n"
                f"■ URL: {alert_data.get('source_url', 'N/A')}\n"
                f"■ 탐지 시각: {alert_data.get('created_at', 'N/A')}"
            )

            # --- (2단계 기술) 텔레그램 발송 ---
            bot = telegram.Bot(token=TELEGRAM_TOKEN)
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
            print(f"*** 텔레그램 알림 발송 성공: {victim_target} ***")

        else:
            # MENTION 타입이거나 PDF 로직에 맞지 않으면 알림을 보내지 않습니다.
            print(
                f"MENTION 타입이거나 알림 대상 아님. (Type: {alert_data.get('korea_mention_type')})"
            )

    except Exception as e:
        print(f"알림 처리 중 오류 발생: {e}")
    finally:
        # (중요) DB 연결은 어떤 일이 있어도 항상 닫아줍니다.
        if client:
            client.close()
            print("DB 연결을 닫았습니다.")


# -----------------------------------
# 3. 스크립트 실행 지점 (1번 크롤러가 호출할 방식)
# -----------------------------------
if __name__ == "__main__":
    try:
        # 1번 팀원이 터미널의 첫 번째 파라미터로 ID를 넘겨줄 것입니다.
        # (예: python alerter.py 68f6164ae5d33d3b32b27fb0)
        target_id = sys.argv[1]
    except IndexError:
        print("=" * 50)
        print("오류: 호출 시 ID를 파라미터로 넘겨주어야 합니다.")
        print("예: python alerter.py [MongoDB ID]")
        print("=" * 50)
        sys.exit(1)  # 오류로 종료

    print(f"--- 알림 시스템(alerter.py) 시작 (Target ID: {target_id}) ---")

    # 2단계에서 배운 비동기 함수(send_alert_for_id)를 실행합니다.
    asyncio.run(send_alert_for_id(target_id))

    print("--- 알림 시스템(alerter.py) 작업 완료 ---")


# --------------------초기 코드 (삭제해도 상관 x) --------------------#
# import telegram  # 텔레그램 라이브러리 (pip로 설치한)
# import asyncio  # 최신 텔레그램 라이브러리는 비동기(async) 방식이 필요

# # --- 1. 설정: 방금 얻은 '비밀번호'와 '주소' ---
# # (절대 이 파일을 GitHub에 올리지 마세요!)
# MY_TOKEN = "REMOVED_TELEGRAM_TOKEN"
# MY_CHAT_ID = -4983996816  # 여기에 Step 2.2에서 찾은 Chat ID (숫자)를 넣으세요


# async def send_hello_world():
#     """
#     텔레그램 봇을 통해 'Hello World' 메시지를 보냅니다.
#     """
#     try:
#         # 1. '웨이터(Bot)' 객체를 내 '회원증(Token)'으로 생성
#         bot = telegram.Bot(token=MY_TOKEN)

#         # 2. '메뉴판(API)'에서 '메시지 보내기' 기능 호출
#         # (chat_id = 주소, text = 내용)
#         await bot.send_message(
#             chat_id=MY_CHAT_ID, text="[K-MONITOR 테스트] Hello World! API 연동 성공!"
#         )

#         print(">>> 메시지 전송 성공! 텔레그램을 확인하세요.")

#     except Exception as e:
#         print(f">>> 메시지 전송 실패: {e}")
#         print(
#             ">>> API 토큰과 Chat ID가 정확한지, 봇이 그룹방에 초대되었는지 확인하세요."
#         )


# # --- 스크립트 실행 ---
# if __name__ == "__main__":
#     # 비동기 함수(send_hello_world)를 실행시킵니다.
#     asyncio.run(send_hello_world())
