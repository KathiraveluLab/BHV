from datetime import datetime, timezone

import bcrypt
from bson import ObjectId
from bson.errors import InvalidId

from database import get_db


class User:
    collection_name = "users"

    @staticmethod
    def _collection():
        return get_db()[User.collection_name]

    @staticmethod
    def create_user(email, password):
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        doc = {
            "email": email,
            "password": hashed,
            "created_at": datetime.now(timezone.utc),
        }
        User._collection().insert_one(doc)
        return doc

    @staticmethod
    def get_by_email(email):
        return User._collection().find_one({"email": email})

    @staticmethod
    def get_by_id(user_id):
        try:
            return User._collection().find_one({"_id": ObjectId(user_id)})
        except (InvalidId, TypeError):
            return None

    @staticmethod
    def check_password(user, password):
        return bcrypt.checkpw(password.encode("utf-8"), user["password"])
