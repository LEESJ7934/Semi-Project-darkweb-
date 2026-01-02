import json  # JSON 처리를 위해 추가
import pandas as pd
from django.shortcuts import render
from pymongo import MongoClient


# Plotly 관련 import는 모두 제거됨

def latest_data_table(request):
    # MongoDB 연결 정보
    client = MongoClient('REMOVED_MONGODB_URI')
    db = client['djongo_database']
    collection = db['clawling_data']

    # 1. 데이터 조회
    latest_companies = list(collection.find(
        {}
    ).sort('scraped_time', -1).limit(20))

    # 2. 데이터프레임 변환 및 Chart.js용 JSON 생성
    df = pd.DataFrame(latest_companies)

    chart_data_json = '{}'  # 기본값은 빈 JSON 문자열

    # 데이터가 있을 경우 JSON 생성
    if not df.empty and 'company_name' in df.columns:
        # 1. 빈도수 집계
        name_counts = df['company_name'].value_counts().reset_index()
        name_counts.columns = ['company_name', 'count']

        # 빈도수 높은 순으로 정렬
        name_counts = name_counts.sort_values(by='count', ascending=False)

        # 2. Chart.js가 사용할 labels (회사 이름)과 data (빈도수) 추출
        labels = name_counts['company_name'].tolist()
        data = name_counts['count'].tolist()

        # 3. JSON 형식으로 변환 (템플릿으로 전달)
        chart_data = {
            'labels': labels,
            'data': data
        }
        chart_data_json = json.dumps(chart_data)

    context = {
        'data_list': latest_companies,
        'chart_data_json': chart_data_json  # Chart.js가 사용할 JSON 데이터 전달
    }

    print(f"--- 데이터베이스 조회 결과: 총 {len(latest_companies)}개 데이터 조회 ---")
    print("--- Chart.js JSON Data (일부) ---")
    print(chart_data_json[:100] + "...")  # JSON 데이터 확인
    print("--------------------------")

    return render(request, 'mongoDbConnect/table.html', context)