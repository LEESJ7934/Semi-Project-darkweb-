import json
import os
from collections import Counter
from pathlib import Path

from django.shortcuts import render
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

COLLECTION_NAME = "leaked_data"


def latest_data_table(request):
    context = {
        "data_list": [],
        "chart_data_json": "{}",
        "database_error": None,
    }

    mongo_uri = os.getenv("DB_URI", "").strip()
    db_name = os.getenv("DB_NAME", "darkweb").strip()

    if not mongo_uri:
        context["database_error"] = (
            "DB_URI 환경변수가 설정되지 않았습니다."
        )
        return render(
            request,
            "mongoDbConnect/table.html",
            context,
        )

    client = None

    try:
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
        )
        client.admin.command("ping")

        collection = client[db_name][COLLECTION_NAME]

        latest_companies = list(
            collection.find({})
            .sort("scraped_time", -1)
            .limit(100)
        )

        name_counts = Counter(
            str(item.get("company_name") or "unknown")
            for item in latest_companies
        )
        most_common_names = name_counts.most_common()

        chart_data = {
            "labels": [
                name
                for name, _ in most_common_names
            ],
            "data": [
                count
                for _, count in most_common_names
            ],
        }

        context["data_list"] = latest_companies
        context["chart_data_json"] = json.dumps(
            chart_data,
            ensure_ascii=False,
        )

        print(
            "MongoDB 조회 성공: "
            f"{len(latest_companies)}개 문서"
        )

    except PyMongoError as error:
        context["database_error"] = (
            "MongoDB에서 데이터를 불러오지 못했습니다."
        )
        print(
            "MongoDB 조회 실패: "
            f"{type(error).__name__}"
        )

    finally:
        if client is not None:
            client.close()

    return render(
        request,
        "mongoDbConnect/table.html",
        context,
    )