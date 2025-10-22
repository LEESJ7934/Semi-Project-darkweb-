from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from elasticsearch import Elasticsearch
from zoneinfo import ZoneInfo
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from dotenv import load_dotenv
import os, datetime
import hashlib
# .env 파일 불러오기
load_dotenv()

# 환경변수 읽기
MONGO_URI = os.getenv("ATLAS_URI")
DB_NAME = os.getenv("DB_NAME")

# MongoDB 연결
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "chromedriver/chromedriver.exe")
service = Service(CHROMEDRIVER_PATH)
#동적 크롤링
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
chrome_options = Options()
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9150")

service = Service(CHROMEDRIVER_PATH)
now_kst = datetime.datetime.now(ZoneInfo("Asia/Seoul"))
driver = webdriver.Chrome(service=service, options=chrome_options)

############################################## 크롤링 공통 코드#################################################################


driver.get("http://gunrabxbig445sjqa535uaymzerj6fp4nwc6ngc2xughf2pedjdhk4ad.onion/")
time.sleep(1)



contents = driver.find_elements(By.CLASS_NAME, "tile")

for i in contents:
    try:
        data_contents = i.find_element(By.CSS_SELECTOR, "ul > li > a").text.strip()
        print(data_contents)
    except NoSuchElementException:
        data_contents = "unknown"  # 없을 경우 None 또는 "" 등으로 처리
        print(data_contents)
    
