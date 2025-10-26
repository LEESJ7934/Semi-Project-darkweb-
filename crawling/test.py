from pymongo import MongoClient

client = MongoClient("REMOVED_MONGODB_URI")
print(client.list_database_names())