from pymongo import MongoClient

client = MongoClient("mongodb://adminUser:root@localhost:27017/")
print(client.list_database_names())