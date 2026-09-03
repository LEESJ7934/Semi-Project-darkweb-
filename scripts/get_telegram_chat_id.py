import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

telegram_token = os.getenv("TELEGRAM_TOKEN")

if not telegram_token:
    raise SystemExit(
        ".env에 TELEGRAM_TOKEN이 설정되지 않았습니다."
    )

request_url = (
    f"https://api.telegram.org/"
    f"bot{telegram_token}/getUpdates"
)

try:
    with urlopen(request_url, timeout=10) as response:
        result = json.load(response)
except (HTTPError, URLError, TimeoutError):
    raise SystemExit(
        "Telegram API 요청에 실패했습니다. "
        "새 토큰이 올바른지 확인하세요."
    )

found = False

for update in result.get("result", []):
    message = (
        update.get("message")
        or update.get("channel_post")
    )

    if not message:
        continue

    chat = message.get("chat", {})
    chat_type = chat.get("type")

    if chat_type not in {"group", "supergroup"}:
        continue

    print(
        f"그룹 이름: {chat.get('title', 'unknown')}"
    )
    print(
        f"TELEGRAM_CHAT_ID={chat.get('id')}"
    )
    found = True

if not found:
    print(
        "그룹 정보를 찾지 못했습니다. "
        "그룹에서 /start를 보낸 뒤 다시 실행하세요."
    )