# alerter.py (V3.0 최종 완성본)

import os
import sys
import asyncio
from telegram import Bot # 텔레그램 라이브러리
from pymongo import MongoClient  # MongoDB 라이브러리
from dotenv import load_dotenv  # .env 파일 로더
import datetime  # 날짜/시간 처리를 위함
import time  # sleep 함수를 위함

# -----------------------------------
# 1. 설정 로드 (.env 파일 사용)
# -----------------------------------
load_dotenv()  # .env 파일의 내용을 환경 변수로 로드


# 환경 변수에서 설정값 읽기 (올바른 방식)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # <-- .env 파일의 변수 '이름' 사용
TELEGRAM_CHAT_ID_STR = os.getenv("TELEGRAM_CHAT_ID")  # <-- .env 파일의 변수 '이름' 사용
MONGO_CONN_STR = os.getenv("DB_URI")  # <-- .env 파일의 변수 '이름' 사용
DB_NAME = os.getenv("DB_NAME")  # <-- .env 파일의 변수 '이름' 사용
COLLECTION_NAME = "leaked_data"  # 직접 지정

# (필수) 설정값이 로드되었는지 확인 및 Chat ID 숫자 변환
if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID_STR, MONGO_CONN_STR, DB_NAME]):
    print("!!!.env 파일에 필요한 환경 변수가 설정되지 않았습니다.")
    print("필수 변수: TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, DB_URI, DB_NAME")
    sys.exit(1)  # 설정 없으면 스크립트 강제 종료
try:
    TELEGRAM_CHAT_ID = int(TELEGRAM_CHAT_ID_STR)  # Chat ID는 정수여야 함
except ValueError:
    print(
        f"!!! 치명적 오류: .env 파일의 TELEGRAM_CHAT_ID ('{TELEGRAM_CHAT_ID_STR}')가 올바른 숫자가 아닙니다."
    )
    sys.exit(1)


# -----------------------------------
# 2. 위험도 분류 함수 (classify_risk) - 개선 완료
# -----------------------------------
def classify_risk(data: dict):
    """
    MongoDB 데이터를 기반으로 '계층적 위험도'를 분류합니다.
    등급(level), 사유(reason), 공격자(actor)를 반환합니다.
    """
    if not isinstance(data, dict):  # 데이터 타입 방어 코드
        return "ERROR", "Invalid data format", "unknown"

    # 1. 데이터 정제 (Cleaning)
    actor_id = data.get("_id")
    actor = "unknown"  # 기본값
    # 개선 1: _id가 문자열이고 '_' 포함 시에만 actor 추출 시도
    if isinstance(actor_id, str) and "_" in actor_id:
        try:
            actor = actor_id.split("_")[0]
        except Exception:
            pass  # 오류 발생 시 기본값 'unknown' 유지

    country = (
        str(data.get("country", "unknown"))
        .lower()
        .replace("🗺️", "")
        .replace("location:", "")
        .strip()
    )

    contents = str(data.get("data_contents", "unknown")).lower()  # 현재 오타 반영
    data_size = str(data.get("data_size", "unknown")).lower()
    company_name = str(data.get("company_name", "unknown")).lower()
    company_url = (
        str(data.get("company_url", "unknown")).lower().replace("🔗", "").strip()
    )
    description = str(data.get("description", "unknown")).lower()

    # 2. 주요 기반시설(Tier 1, 2) 렉시콘 정의 (지속적 업데이트 필요)
    TIER_1_VICTIMS = ["government", "defense", "국방", "정부", "military"]
    TIER_2_VICTIMS = [
        "sk shieldus",
        "ahnlab",
        "kdb",
        "woori",
        "samsung life",
        "medical",
        "hospital",
        "finance",
        "bank",
        "kaspersky",
        "lg cns",
        "sds",
        "보안",
        "금융",
        "의료",
    ]

    # 3. 민감 데이터 키워드 렉시콘 정의
    CRITICAL_KEYWORDS = [
        "billing",
        "customer data",
        "personal document",
        "patient data",
        "계좌",
        "결제",
        "주민등록",
        "여권",
        "ssn",
    ]
    HIGH_KEYWORDS = [
        "financial document",
        "internal document",
        "employee data",
        "재무",
        "회계",
        "인사",
        "contract",
        "agreement",
    ]
    # 개선 2 반영: 한국 기업명 키워드 렉시콘
    KOREAN_COMPANY_KEYWORDS = [
        "samsung",
        "lg",
        "hyundai",
        "sk",
        "kt",
        "cj",
        "lotte",
        "posco",
        "hanwha",
    ]  # 예시 확장

    # --- 4. 계층적 분류(Triage) 시작 ---

    # 1순위: 'CRITICAL' 민감 데이터
    if any(keyword in contents for keyword in CRITICAL_KEYWORDS):
        return "CRITICAL", f"민감 정보 유출 의심 ({contents[:30]}...)", actor

    # 2순위: 'CRITICAL' 주요 기반시설 또는 한국 '확정' (.kr 도메인)
    if "korea" in country or "south korea" in country or company_url.endswith(".kr"):
        return "CRITICAL", f"한국 직접 확정 ({country or company_url})", actor
    if any(victim in company_name for victim in TIER_1_VICTIMS):
        return "CRITICAL", f"Tier 1(정부/국방) 의심 ({company_name})", actor
    if any(victim in company_name for victim in TIER_2_VICTIMS):
        return "CRITICAL", f"Tier 2(주요 기반) 의심 ({company_name})", actor

    # 3순위: 'HIGH' 고가치 데이터
    if any(keyword in contents for keyword in HIGH_KEYWORDS):
        return "HIGH", f"주요 문서 유출 의심 ({contents[:30]}...)", actor

    # 4순위: 'HIGH' 대규모 유출
    if "tb" in data_size:
        return "HIGH", f"대규모(TB) 유출 ({data_size})", actor

    # 5순위: 'MEDIUM' 한국 '의심' (기업명 키워드 또는 .co.kr 도메인) - 개선 2 순서 반영
    if any(kw in company_name for kw in KOREAN_COMPANY_KEYWORDS):
        return "MEDIUM", f"한국 기업명 의심 ({company_name})", actor
    elif ".co.kr" in company_url:
        return "MEDIUM", f"한국 도메인 의심 ({company_url})", actor

    # 6순위: 'LOW' 간접 언급 (description 필드 사용)
    if any(kw in description for kw in KOREAN_COMPANY_KEYWORDS):
        return "LOW", "간접 언급 (알림 미발송)", actor

    # 모든 조건 불충족 시
    return "INFO", "한국 관련성 낮음", actor


# -----------------------------------
# 3. 텔레그램 메시지 포매팅 함수 (format_telegram_message)
# -----------------------------------
def format_telegram_message(data: dict, level: str, reason: str, actor: str):
    """classify_risk 결과를 바탕으로 세분화된 텔레그램 알림 메시지를 생성합니다."""

    level_emoji = {"CRITICAL": "🚨", "HIGH": "🔥", "MEDIUM": "⚠️", "LOW": "ℹ️"}
    title = (
        f"[{level_emoji.get(level, '❓')} {level}] {data.get('company_name', 'N/A')}"
    )

    # scraped_time 필드 처리
    scraped_time_str = "N/A"
    scraped_time_obj = data.get("scraped_time")
    try:
        dt_utc = None
        if isinstance(scraped_time_obj, datetime.datetime):
            dt_utc = scraped_time_obj.replace(tzinfo=datetime.timezone.utc)
        elif isinstance(scraped_time_obj, dict) and "$date" in scraped_time_obj:
            dt_utc = datetime.datetime.fromisoformat(
                scraped_time_obj["$date"].replace("Z", "+00:00")
            )

        if dt_utc:
            dt_kst = dt_utc.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
            scraped_time_str = dt_kst.strftime("%Y-%m-%d %H:%M:%S KST")
    except Exception as e:
        print(f"시간 변환 오류: {e}, 원본: {scraped_time_obj}")
        scraped_time_str = str(scraped_time_obj)

    # 개선 5 주석: 1번 팀원이 data_contetns 오타 수정 시 아래 코드로 변경 필요
    # f"■ 유출 내용: {data.get('data_contents', 'unknown')}\n" # 오타 수정 시
    message = (
        f"{title}\n"
        f"----------------------------------------\n"
        f"■ 위험도: {level} ({reason})\n"
        f"■ 공격자: {actor.upper()}\n"
        f"■ 피해 규모: {data.get('data_size', 'unknown')}\n"
        f"■ 유출 내용: {data.get('data_contents', 'unknown')}\n"  # 현재 오타 반영
        f"■ 국가: {data.get('country', 'unknown')}\n"
        f"■ URL: {data.get('company_url', 'unknown')}\n"
        f"■ 탐지 시각: {scraped_time_str}"
    )
    return message


# -----------------------------------
# 4. 텔레그램 발송 함수 (send_telegram_alert)
# -----------------------------------
async def send_telegram_alert(message: str):
    """텔레그램으로 알림 메시지를 비동기 발송합니다."""
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print(">>> 텔레그램 알림 발송 성공")
    except Exception as e:
        print(f"!!! 텔레그램 발송 오류 (BadRequest): {e}")
        print(
            ">>> .env 파일의 Chat ID가 올바른지, 봇이 그룹방에 초대되었는지 확인하세요."
        )
    except Exception as e:
        print(f"!!! 텔레그램 발송 중 예상치 못한 오류: {e}")

# -----------------------------------
# 5. 메인 감시자 함수 (main_watcher) - 개선 완료
# -----------------------------------
def main_watcher():
    """MongoDB 'leaked_data' 컬렉션을 24시간 감시하고 알림을 보냅니다."""
    client = None
    print(
        f">>> 알림 시스템(V3.0) 시작: {DB_NAME}.{COLLECTION_NAME} 컬렉션을 감시합니다..."
    )
    print(f"MongoDB URI: {MONGO_CONN_STR[:15]}...{MONGO_CONN_STR[-5:]}")

    while True:
        try:
            client = MongoClient(MONGO_CONN_STR)
            client.admin.command("ping")  
            print(">>> MongoDB 서버에 성공적으로 연결되었습니다.")

            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]

            pipeline = [{"$match": {"operationType": "insert"}}]
            with collection.watch(
                pipeline, full_document="updateLookup"
            ) as stream: 
                print(">>> Change Stream 감시 시작. 새 데이터 삽입 대기 중...")
                for change_event in stream:
                    print(
                        f"\n--- 새 위협 감지 (ID: {change_event['documentKey']['_id']}) ---"
                    )
                    new_data = change_event.get("fullDocument")

                    if not new_data:
                        print(
                            "  [!] fullDocument 누락 (MongoDB 설정 확인 필요). 이벤트 스킵."
                        )
                        continue

                    # 위험도 분류
                    level, reason, actor = classify_risk(new_data)

                    # 알림 발송 조건 확인 및 실행
                    if level in ["CRITICAL", "HIGH", "MEDIUM"]:
                        print(
                            f"  [!] 등급: {level} / 사유: {reason} / 공격자: {actor.upper()}"
                        )
                        message = format_telegram_message(
                            new_data, level, reason, actor
                        )
                        # 개선 3: asyncio.run() 유지 (호환성 및 간결성 위해)
                        asyncio.run(send_telegram_alert(message))
                    else:
                        print(f"  [.] 등급: {level} (알림 미발송)")

        except KeyboardInterrupt:
            print("\n>>> 감시자(Watcher)가 수동으로 종료되었습니다.")
            break  # while 루프 탈출
        except Exception as e:
            print(f"!!! MongoDB Watcher 또는 처리 중 오류 발생: {e}")
            print("10초 후 재연결을 시도합니다...")
            if client:
                client.close()
            # 개선 4: time.sleep 사용
            time.sleep(10)  # 10초 대기 후 루프 재시작

    if client:
        client.close()
        print(">>> MongoDB 연결을 최종적으로 닫았습니다.")


# -----------------------------------
# 6. 스크립트 실행
# -----------------------------------
if __name__ == "__main__":
    main_watcher()  # Watcher 함수 실행