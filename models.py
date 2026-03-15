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
    def create_user(name, email, password):
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        doc = {
            "name": name,
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


class Upload:
    collection_name = "uploads"

    @staticmethod
    def _collection():
        return get_db()[Upload.collection_name]

    @staticmethod
    def create(
        user_id,
        title,
        description,
        filename,
        sentiment,
        custom_sentiment=None,
        voice_note_filename=None,
    ):
        doc = {
            "user_id": ObjectId(user_id),
            "title": title,
            "description": description,
            "filename": filename,
            "sentiment": sentiment,
            "custom_sentiment": custom_sentiment,
            "voice_note_filename": voice_note_filename,
            "created_at": datetime.now(timezone.utc),
        }
        Upload._collection().insert_one(doc)
        return doc

    @staticmethod
    def get_by_user(user_id):
        try:
            return list(
                Upload._collection()
                .find({"user_id": ObjectId(user_id)})
                .sort("created_at", -1)
            )
        except (InvalidId, TypeError):
            return []

    @staticmethod
    def get_by_id(upload_id):
        try:
            return Upload._collection().find_one({"_id": ObjectId(upload_id)})
        except (InvalidId, TypeError):
            return None
