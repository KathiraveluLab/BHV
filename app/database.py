from pymongo import MongoClient

from .config import DATABASE_NAME, MONGO_URI


client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

users_collection = db["users"]
images_collection = db["images"]
