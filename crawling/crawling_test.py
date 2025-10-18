import requests
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# 정적 웹 사이트
# # .onion 사이트 URL
# url = "http://rnsm777cdsjrsdlbs4v5qoeppu3px6sb2igmh53jzrx7ipcrbjz5b2ad.onion/"

# # 헤더 (Selenium에서 쓰던 User-Agent 그대로 유지)
# headers = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/73.0.3683.86 Safari/537.36"
#     )
# }

# # Tor Proxy 설정 (SOCKS5h — DNS도 Tor를 통해 처리)
# proxies = {
#     "http": "socks5h://127.0.0.1:9150",
#     "https": "socks5h://127.0.0.1:9150"
# }

# # 요청
# response = requests.get(url, headers=headers, proxies=proxies, timeout=60)

# html_text = response.text

# soup = bs(response.text, 'html.parser')

# dark_contents = soup.find_all("li")

# for li in dark_contents:
#     print(li.text.strip())





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