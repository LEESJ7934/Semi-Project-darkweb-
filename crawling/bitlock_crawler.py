
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from datetime import datetime, timezone, timedelta
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import hashlib
# .env 파일 불러오기
load_dotenv()

# 환경변수 읽기
MONGO_URI = os.getenv("DB_URI")
DB_NAME = os.getenv("DB_NAME")

# MongoDB 연결
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver", "chromedriver.exe")
service = Service(CHROMEDRIVER_PATH)
#동적 크롤링
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
chrome_options = Options()
chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9150")

service = Service(CHROMEDRIVER_PATH)

now_utc = datetime.now(timezone.utc)
real_time = now_utc + timedelta(hours=9)
driver = webdriver.Chrome(service=service, options=chrome_options)

############################################## 크롤링 공통 코드#################################################################

driver.get("http://lockbit3753ekiocyo5epmpy6klmejchjtzddoekjlnt6mu3qh4de2id.onion/")  
time.sleep(15)

contents = driver.find_elements(By.CSS_SELECTOR, ".post-block.good")
collection = db['leaked_data']
count = 0

try:
    for i in contents:
        try:
            if count >= 50:
                break;
            company_overview_text = i.find_element(By.CSS_SELECTOR, "div:nth-of-type(1)").text.strip()
            parts = company_overview_text.replace("published", "").split("\n")
            # URL에서 회사 이름과 도메인을 분리
            company_url = parts[0].strip()
            # URL에서 회사 이름과 도메인을 분리
            company_name = company_url.split('.')[0].strip()  # .com, .net 등 앞부분 추출 
            description = i.find_element(By.CSS_SELECTOR, "div.post-block-text").text.strip()
            publication_date = i.find_element(By.CSS_SELECTOR, "div.updated-post-date").text.strip().replace("Updated:","")
            raw_id = f"{company_url}_{description}_{publication_date}"
            hash_id = hashlib.md5(raw_id.encode("utf-8")).hexdigest()
            count+=1
            doc = {
                "_id": "bitlock_" + hash_id,
                "scraped_time": real_time,

                "company_name": company_name,
                "company_url" : company_url,
                "country"    : "unknown",

                "data_contetns" : "unknown",
                "data_size" : "unknown",
                "publication_date" : publication_date,

                "description" : description, 

                }
            
        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")

        collection.update_one(
            {"_id": doc["_id"]},  
            {"$set": doc},       
            upsert=True           
            )
        
        
    print(" -> Saved to MongoDB")
except Exception as e:
    print(" -> MongoDB insert error:", e)