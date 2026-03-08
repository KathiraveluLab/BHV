import os

from pymongo import MongoClient

uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/bhv")
_client = MongoClient(uri)


def get_db():
    return _client.get_default_database()


def close_db():
    _client.close()
