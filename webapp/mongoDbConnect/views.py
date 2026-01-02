import json
import pandas as pd
from django.shortcuts import render
from pymongo import MongoClient
from dotenv import load_dotenv
import os,sys
# .env 파일 불러오기
load_dotenv()

# 환경 변수 읽기\

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from alert.alert import classify_risk

MONGO_URI = os.getenv("DB_URI")
DB_NAME = os.getenv("DB_NAME")


def latest_data_table(request):
    # MongoDB 연결
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db["leaked_data"]

    # 1. 데이터 조회
    latest_companies = list(
        collection.find({}).sort("scraped_time", -1).limit(100)
    )

    # 2. 위험도 분류 적용
    risk_levels = []
    for doc in latest_companies:
        try:
            level, reason, actor = classify_risk(doc)
            doc["risk_level"] = level
            doc["risk_reason"] = reason
            doc["risk_actor"] = actor
            risk_levels.append(level)
        except Exception as e:
            print(f"⚠️ classify_risk 처리 오류: {e}")
            doc["risk_level"] = "ERROR"
            risk_levels.append("ERROR")

    # 3. 위험도별 빈도 집계 (pandas 이용)
    df = pd.DataFrame(latest_companies)

    chart_data_json = "{}"  # 기본값

    if not df.empty and "risk_level" in df.columns:
        risk_counts = df["risk_level"].value_counts().reset_index()
        risk_counts.columns = ["risk_level", "count"]

        # Chart.js용 데이터 변환
        labels = risk_counts["risk_level"].tolist()
        data = risk_counts["count"].tolist()

        # 위험도 색상 (Chart.js용)
        color_map = {
            "CRITICAL": "rgba(255, 0, 0, 0.6)",
            "HIGH": "rgba(255, 100, 0, 0.6)",
            "MEDIUM": "rgba(255, 200, 0, 0.6)",
            "LOW": "rgba(0, 150, 255, 0.6)",
            "INFO": "rgba(200, 200, 200, 0.6)",
            "ERROR": "rgba(120, 120, 120, 0.4)",
        }
        background_colors = [color_map.get(lv, "rgba(150,150,150,0.5)") for lv in labels]

        chart_data = {
            "labels": labels,
            "data": data,
            "background_colors": background_colors,
        }
        chart_data_json = json.dumps(chart_data)

    # 4. 템플릿 컨텍스트
    context = {
        "data_list": latest_companies,
        "chart_data_json": chart_data_json,
    }

    print(f"--- MongoDB에서 {len(latest_companies)}개 문서 조회 ---")
    print(f"--- Chart Data 예시: {chart_data_json[:100]}...")

    return render(request, "mongoDbConnect/table.html", context)
