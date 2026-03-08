import os

from pymongo import MongoClient

_client = None


def get_db():
    global _client
    if _client is None:
        uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/bhv")
        _client = MongoClient(uri)
    return _client.get_default_database()


def close_db():
    global _client
    if _client is not None:
        _client.close()
        _client = None
