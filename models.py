import uuid6
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import Database

class User:
    def __init__(self, name, email, password=None, role='user', google_id=None):
        self.user_id = str(uuid6.uuid7())
        self.name = name
        self.email = email
        self.password = generate_password_hash(password) if password else None
        self.role = role
        self.google_id = google_id
        self.created_at = datetime.now()

    @staticmethod
    def find_by_email(email):
        if not isinstance(email, str): return None
        db = Database.get_db()
        return db.users.find_one({"email": email.strip().lower()})

    @staticmethod
    def find_by_id(user_id):
        if not isinstance(user_id, str): return None
        db = Database.get_db()
        return db.users.find_one({"user_id": user_id}, {"_id": 0})

    @staticmethod
    def find_by_google_id(google_id):
        db = Database.get_db()
        return db.users.find_one({"google_id": google_id})

    @staticmethod
    def verify_password(stored_password, provided_password):
        if stored_password is None: return False
        return check_password_hash(stored_password, provided_password)

    @staticmethod
    def create_user(name, email, password):
        db = Database.get_db()
        normalized_email = email.strip().lower()
        if User.find_by_email(normalized_email): return False
        
        new_user = User(name, normalized_email, password)
        user_to_save = {
            "user_id": new_user.user_id,
            "name": new_user.name,
            "email": new_user.email,
            "password": new_user.password,
            "role": new_user.role,
            "google_id": None,
            "created_at": new_user.created_at
        }
        db.users.insert_one(user_to_save)
        return True

    @staticmethod
    def create_google_user(name, email, google_id):
        db = Database.get_db()
        normalized_email = email.strip().lower()
        new_user = User(name, normalized_email, google_id=google_id)
        user_to_save = {
            "user_id": new_user.user_id,
            "name": new_user.name,
            "email": new_user.email,
            "password": None, 
            "role": new_user.role,
            "google_id": google_id,
            "created_at": new_user.created_at
        }
        db.users.insert_one(user_to_save)
        return user_to_save 

    @staticmethod
    def set_password(user_id, new_password):
        db = Database.get_db()
        hashed_password = generate_password_hash(new_password)
        result = db.users.update_one(
            {"user_id": user_id},
            {"$set": {"password": hashed_password}}
        )
        return result.modified_count > 0

    @staticmethod
    def get_all_users():
        db = Database.get_db()
        return list(db.users.find({}, {"name": 1, "user_id": 1, "email": 1,"role": 1, "_id": 0}))

class Image:
    @staticmethod
    def save_metadata(user_id, username, uploaded_by, uploader_name, filename, 
                     description, sentiment, github_url, ai_description="", file_size=0, file_type="image/jpeg",is_verified=False,uploader_role="user"):
        if is_verified:
            db = Database.get_db()
            image_data = {
                "upload_id":  str(uuid6.uuid7()),
                "uploader_role":uploader_role,
                "user_id": user_id, 
                "username": username,
                "uploaded_by": uploaded_by,
                "uploader_name": uploader_name,
                "filename": filename,
                "github_url": github_url, 
                "file_size": file_size, 
                "file_type": file_type, 
                "description": description,
                "sentiment": sentiment,
                "ai_description": ai_description,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "updated_by": uploaded_by,
                "updated_by_name": uploader_name,
                "is_active": True 
            }
            db.uploads.insert_one(image_data)
            return True
        else:
            return False

    @staticmethod
    def get_user_images(user_id):
        db = Database.get_db()
        return list(db.uploads.find({
            "user_id": user_id, 
            "is_active": True
        }).sort("created_at", -1))

    @staticmethod
    def get_all_images_admin():
        db = Database.get_db()
        return list(db.uploads.find({"is_active": True}).sort("created_at", -1))

    @staticmethod
    def update_image_data(upload_id, modifier_id, modifier_name, new_desc, new_sentiment, new_ai_desc=None):
        db = Database.get_db()
        update_fields = {
            "description": new_desc,
            "sentiment": new_sentiment,
            "updated_at": datetime.now(),
            "updated_by": modifier_id,
            "updated_by_name": modifier_name
        }
        if new_ai_desc is not None:
            update_fields["ai_description"] = new_ai_desc

        return db.uploads.update_one(
            {"upload_id": upload_id},
            {"$set": update_fields}
        )

    @staticmethod
    def get_image_by_id(upload_id):
        db = Database.get_db()
        return db.uploads.find_one({"upload_id": upload_id})

    @staticmethod
    def hard_delete(upload_id):
        db = Database.get_db()
        return db.uploads.delete_one({"upload_id": upload_id}).deleted_count == 1