from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("ATLAS_URI")
print("URI:", uri)

client = MongoClient(uri)
print("✅ Databases:", client.list_database_names())

