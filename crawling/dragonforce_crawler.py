from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from elasticsearch import Elasticsearch
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import datetime
import hashlib
# .env 파일 불러오기
load_dotenv()

# 환경변수 읽기
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# MongoDB 연결
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "chromedriver/chromedriver.exe")
service = Service(CHROMEDRIVER_PATH)
#동적 크롤링
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
chrome_options = Options()
chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9150")

service = Service(CHROMEDRIVER_PATH)

driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("http://z3wqggtxft7id3ibr7srivv5gjof5fwg76slewnzwwakjuf3nlhukdid.onion/blog")
time.sleep(1)

contents = driver.find_elements(By.CLASS_NAME, "publications-list__publication")

collection = db['leaked_data']

try:
    for i in contents:
        try:
            company_names = i.find_element(By.CLASS_NAME, "list-publication__name").text.strip()
            hash_id = hashlib.md5(company_names.encode('utf-8')).hexdigest()
            company_url = i.find_element(By.CSS_SELECTOR, "p.publication-addictional__row a.addiction-row__text.addictional-row__link").text.strip()
            description = i.find_element(By.CLASS_NAME, "list-publication__description").text.strip()
            publication_date = i.find_element(By.CLASS_NAME, "publication-footer__date").text.strip()
            
            doc = {
                "_id": "dragonforce_" + hash_id,
                "company_name": company_names,
                "company_url" : company_url,
                "description" : description,
                "publication_date" : publication_date,     
                "scraped_time": datetime.datetime.utcnow()
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



