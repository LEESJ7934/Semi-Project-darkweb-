from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import subprocess
import datetime
import threading
import os

# --- 실행 함수 ---
def run_crawler(script_name):
    """
    특정 크롤러 스크립트를 subprocess로 실행.
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 상위 폴더 (프로젝트 루트)
        script_path = os.path.join(base_dir, "crawling", script_name)

        subprocess.run(["python", script_path], check=True)

        end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{end}]  실행 완료: {script_name}\n")
    except subprocess.CalledProcessError as e:
        print(f" {script_name} 실행 중 오류 발생: {e}\n")


# 병렬 실행 (스레드) 
def run_in_thread(script_name):
    thread = threading.Thread(target=run_crawler, args=(script_name,))
    thread.start()


# 스케줄러 설정
scheduler = BlockingScheduler()

# 각 사이트별 주기 설정 (분 단위)
scheduler.add_job(
    lambda: run_in_thread("gunra_crawler.py"),
    IntervalTrigger(seconds=30),
    id="gunra_crawler",
    name="Gunra forum crawler "
)

scheduler.add_job(
    lambda: run_in_thread("Black_Shrantac_crawler.py"),
    IntervalTrigger(seconds=30),
    id="black_shrantac_crawler",
    name="Black Shrantac crawler "
)

scheduler.add_job(
    lambda: run_in_thread("dragonforce_crawler.py"),
    IntervalTrigger(seconds=30),
    id="dragonforce_crawler",
    name="Dragonforce crawler "
)

scheduler.add_job(
    lambda: run_in_thread("bitlock_crawler.py"),
    IntervalTrigger(seconds=30),
    id="bitlock_crawler",
    name="Bitlock crawler "
)

print(" 다크웹 크롤링 스케줄러 시작\n(종료하려면 Ctrl + C)")

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    print("\n 스케줄러 종료됨.")