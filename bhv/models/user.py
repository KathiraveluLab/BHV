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
    github_repo_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    images = db.relationship('Image', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role.value,
            'created_at': self.created_at.isoformat()
        }