import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class Database:
    _client = None

    @staticmethod
    def get_db():
        if Database._client is None:
            Database._client = MongoClient(os.getenv("MONGO_URI"))
        return Database._client['new_bhv_db']