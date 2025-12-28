"""Image model for storing patient images."""
from bhv.database import db
from datetime import datetime
from enum import Enum

class StorageType(Enum):
    LOCAL = "local"
    GITHUB = "github"

class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    storage_type = db.Column(db.Enum(StorageType), default=StorageType.LOCAL, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    file_hash = db.Column(db.String(64), index=True)  # SHA-256 for duplicate detection
    thumbnail_path = db.Column(db.String(500))
    
    # Relationships
    narratives = db.relationship('Narrative', backref='image', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Image {self.id} - {self.file_path}>'
    
    def to_dict(self):
        """Convert image to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_path': self.file_path,
            'storage_type': self.storage_type.value,
            'upload_date': self.upload_date.isoformat(),
            'file_size': self.file_size
        }