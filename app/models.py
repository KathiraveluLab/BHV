"""Database models and user class."""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import bcrypt


def get_db():
    """Get database instance from extensions."""
    from app.extensions import db
    if db is None:
        # Try to initialize if not already done
        try:
            from flask import current_app
            from app.extensions import init_mongodb
            init_mongodb(current_app)
            from app.extensions import db as db_instance
            return db_instance
        except RuntimeError:
            # No application context, db should be initialized by app factory
            raise RuntimeError("Database not initialized. Ensure init_mongodb() is called in create_app().")
    return db


class User(UserMixin):
    """User model for authentication."""
    
    def __init__(self, user_data):
        """Initialize user from MongoDB document."""
        self.id = str(user_data.get('_id'))
        # Normalize email to lowercase for consistent comparison
        email = user_data.get('email', '')
        self.email = email.strip().lower() if email else ''
        self.password_hash = user_data.get('password_hash')
        self._role = user_data.get('role', 'user')  # Stored role
        self.is_verified = user_data.get('is_verified', False)
        self.google_id = user_data.get('google_id')
        self.created_at = user_data.get('created_at', datetime.utcnow())
    
    @property
    def role(self):
        """
        Dynamic role property that checks ADMIN_EMAILS at runtime.
        If email is in ADMIN_EMAILS list, returns 'admin', otherwise returns stored role.
        Always reads ADMIN_EMAILS fresh from .env file at runtime.
        """
        from app.config import is_admin_email
        # Always check fresh from .env file
        if is_admin_email(self.email):
            return 'admin'
        return self._role
    
    def get_stored_role(self):
        """Get the stored role from database (for reference)."""
        return self._role
    
    def is_admin(self):
        """
        Check if user is admin (checks ADMIN_EMAILS dynamically at runtime).
        This method always reflects the current ADMIN_EMAILS configuration.
        Always reads ADMIN_EMAILS fresh from .env file.
        """
        from app.config import is_admin_email
        # Always check fresh from .env file first
        if is_admin_email(self.email):
            return True
        # Also check stored role as fallback
        return self._role == 'admin'
    
    @staticmethod
    def create(email, password=None, role=None, google_id=None):
        """
        Create a new user.
        Role is automatically determined from ADMIN_EMAILS in config.
        If email is in ADMIN_EMAILS list, role is set to 'admin', otherwise 'user'.
        If role is explicitly provided, it will be used.
        """
        from app.config import is_admin_email
        
        # Normalize email for consistent comparison
        normalized_email = email.strip().lower() if email else ''
        
        # Determine role: check if email is in admin emails list, or use provided role, or default to 'user'
        if role is None:
            if is_admin_email(normalized_email):
                role = 'admin'
            else:
                role = 'user'
        
        # Debug logging (can be disabled in production)
        try:
            from flask import current_app
            if current_app and current_app.debug:
                current_app.logger.debug(f"Creating user: email={normalized_email}, role={role}, is_admin_check={is_admin_email(normalized_email)}")
        except:
            pass  # Ignore if no app context
        
        user_data = {
            'email': normalized_email,
            'role': role,
            'is_verified': False,
            'created_at': datetime.utcnow(),
            'google_id': google_id
        }
        
        if password:
            user_data['password_hash'] = bcrypt.hashpw(
                password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
        else:
            user_data['is_verified'] = True  # Google OAuth users are pre-verified
        
        result = get_db().users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    @staticmethod
    def find_by_email(email):
        """Find user by email (case-insensitive)."""
        email = email.strip().lower() if email else None
        if not email:
            return None
        user_data = get_db().users.find_one({'email': email})
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID."""
        try:
            user_data = get_db().users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            pass
        return None
    
    @staticmethod
    def find_by_google_id(google_id):
        """Find user by Google ID."""
        user_data = get_db().users.find_one({'google_id': google_id})
        if user_data:
            return User(user_data)
        return None
    
    def verify(self):
        """Mark user as verified."""
        get_db().users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'is_verified': True}}
        )
        self.is_verified = True
    
    def update_role(self, role):
        """
        Update user's role in database.
        Role should be 'admin' or 'user'.
        """
        get_db().users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'role': role}}
        )
        self._role = role
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'is_verified': self.is_verified
        }


class Upload:
    """Upload model for user content."""
    
    @staticmethod
    def create(user_id, title, description, sentiment, image_file_id, audio_file_id=None):
        """Create a new upload."""
        upload_data = {
            'user_id': user_id,
            'title': title,
            'description': description,
            'sentiment': sentiment,
            'image_file_id': image_file_id,
            'audio_file_id': audio_file_id,
            'created_at': datetime.utcnow()
        }
        result = get_db().uploads.insert_one(upload_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(upload_id):
        """Find upload by ID."""
        try:
            return get_db().uploads.find_one({'_id': ObjectId(upload_id)})
        except:
            return None
    
    @staticmethod
    def find_all(limit=None, skip=0):
        """Find all uploads."""
        query = get_db().uploads.find().sort('created_at', -1).skip(skip)
        if limit:
            query = query.limit(limit)
        return list(query)
    
    @staticmethod
    def find_by_user(user_id):
        """Find all uploads by user."""
        return list(get_db().uploads.find({'user_id': user_id}).sort('created_at', -1))
    
    @staticmethod
    def count_by_sentiment():
        """Count uploads grouped by sentiment."""
        pipeline = [
            {'$group': {
                '_id': '$sentiment',
                'count': {'$sum': 1}
            }}
        ]
        results = list(get_db().uploads.aggregate(pipeline))
        counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        for result in results:
            sentiment = result['_id']
            if sentiment in counts:
                counts[sentiment] = result['count']
        return counts
    
    @staticmethod
    def get_total_count():
        """Get total number of uploads."""
        return get_db().uploads.count_documents({})


class ChatMessage:
    """Chat message model."""
    
    @staticmethod
    def create(user_id, message, sender_role='user'):
        """Create a new chat message."""
        message_data = {
            'user_id': user_id,
            'message': message,
            'sender_role': sender_role,
            'created_at': datetime.utcnow()
        }
        result = get_db().chat_messages.insert_one(message_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_user(user_id):
        """Find all messages for a user."""
        return list(get_db().chat_messages.find({'user_id': user_id}).sort('created_at', 1))
    
    @staticmethod
    def find_all():
        """Find all chat messages (admin only)."""
        return list(get_db().chat_messages.find().sort('created_at', 1))


class OTP:
    """OTP (One-Time Password) model for email verification."""
    
    @staticmethod
    def create(email, otp_code):
        """Create a new OTP record."""
        otp_data = {
            'email': email,
            'otp_code': otp_code,
            'created_at': datetime.utcnow(),
            'used': False
        }
        get_db().otps.insert_one(otp_data)
    
    @staticmethod
    def find_valid(email, otp_code):
        """Find and validate OTP."""
        from datetime import timedelta
        from app.config import Config
        
        expiry_time = datetime.utcnow() - timedelta(minutes=Config.OTP_EXPIRY_MINUTES)
        
        otp_data = get_db().otps.find_one({
            'email': email,
            'otp_code': otp_code,
            'used': False,
            'created_at': {'$gte': expiry_time}
        })
        
        return otp_data is not None
    
    @staticmethod
    def mark_used(email, otp_code):
        """Mark OTP as used."""
        get_db().otps.update_one(
            {'email': email, 'otp_code': otp_code},
            {'$set': {'used': True}}
        )

