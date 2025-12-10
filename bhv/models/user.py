"""User model for authentication and authorization."""
from bhv.database import db
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    PATIENT = "patient"
    SOCIAL_WORKER = "social_worker"
    ADMIN = "admin"


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.PATIENT, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<User {self.email}>'