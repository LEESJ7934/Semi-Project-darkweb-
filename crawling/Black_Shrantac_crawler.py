#black_shrantac 사이트 크롤링
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime, timezone, timedelta
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
collection = db['leaked_data']
############################################## 크롤링 공통 코드#################################################################
driver.get("http://jvkpexgkuaw5toiph7fbgucycvnafaqmfvakymfh5pdxepvahw3xryqd.onion/")

contents = driver.find_elements(By.CLASS_NAME, "book-card")

try:
    for i in contents:
        try:
            company_names = i.find_element(By.CSS_SELECTOR, "div > h3").text.strip()
            company_url = i.find_element(By.CSS_SELECTOR, "div:nth-of-type(3)").text.strip()
            data_size = i.find_element(By.CSS_SELECTOR, "div:nth-of-type(4)").text.strip()
            country = i.find_element(By.CSS_SELECTOR, "div > span").text.strip()
            raw_id = f"{company_names}_{country}_{data_size}"
            hash_id = hashlib.md5(raw_id.encode("utf-8")).hexdigest()
            doc = {
                "_id": "black_shrantac" + hash_id,
                "scraped_time": real_time,

                "company_name": company_names,
                "company_url" : company_url,
                "country"    : country,

                "data_contetns" : "unknown",
                "data_size" : data_size,
                "publication_date" : "unknwon",

                "description" : "unknown", 

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


