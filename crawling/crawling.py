
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import datetime
# .env 파일 불러오기
load_dotenv()

# 환경변수 읽기
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# MongoDB 연결
client = MongoClient(MONGO_URI)
db = client[DB_NAME]


#동적 크롤링
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
chrome_options = Options()
chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9150")
service = Service(
    r"C:\Users\Seung Jun\Desktop\취업 준비 자료\구름 공부 자료\Semi-Project\Semi-Project-darkweb-\chromedriver\chromedriver.exe"
)
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("http://z3wqggtxft7id3ibr7srivv5gjof5fwg76slewnzwwakjuf3nlhukdid.onion/blog")
time.sleep(3)

contents = driver.find_elements(By.CLASS_NAME, "publications-list__publication")
for i in contents:
    content = i.text
    print(content)

collection = db['leaked_data']


doc = {
    "text": content,
    "source": "onion_blog",          
    "scraped_at": datetime.datetime.utcnow()
}

try:
    collection.insert_one(doc)
    print(" -> Saved to MongoDB")
except Exception as e:
    print(" -> MongoDB insert error:", e)