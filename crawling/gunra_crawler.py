#gunra 사이트 크롤링
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

CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "chromedriver/chromedriver.exe")
service = Service(CHROMEDRIVER_PATH)
#동적 크롤링}
chrome_options = Options()

chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9150")

now_utc = datetime.now(timezone.utc)
real_time = now_utc + timedelta(hours=9)
driver = webdriver.Chrome(service=service, options=chrome_options)

############################################## 크롤링 공통 코드#################################################################


driver.get("http://gunrabxbig445sjqa535uaymzerj6fp4nwc6ngc2xughf2pedjdhk4ad.onion/")
time.sleep(1)

contents = driver.find_elements(By.CLASS_NAME, "tile")
collection = db['leaked_data']

try:
    for i in contents:
        try:
            company_names = i.find_element(By.CSS_SELECTOR, "strong a").text.strip()
            parts = company_names.split("|")
            if len(parts) > 1:
                company_name = parts[0]
                data_size = parts[1]
            else:
                company_name = parts[0]
                data_size = "unknown"
            hash_id = hashlib.md5(company_names.encode('utf-8')).hexdigest()
            company_overview_text = i.find_element(By.CSS_SELECTOR, "div:nth-of-type(2)").text.strip()
            parts = company_overview_text.split("|")
            if len(parts) > 2:
                country = parts[1].strip()
                company_url = parts[2].strip()
            else:
                country = "abroad"
                company_url = "unknonn"
            try:
                data_contents = i.find_element(By.CSS_SELECTOR, "ul > li > a").text.strip()
            except NoSuchElementException:
                data_contents = "unknown"  # 없을 경우 None 또는 "" 등으로 처리
            raw_id = f"{company_names}_{data_contents}_{data_size}"
            hash_id = hashlib.md5(raw_id.encode("utf-8")).hexdigest()
            doc = {
                "_id": "gunra_" + hash_id,
                "scraped_time": real_time,

                "company_name": company_name,
                "company_url" : company_url,
                "country"    : country,

                "data_contetns" : data_contents,
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



