from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index, Boolean
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String(50), default='user', index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Add composite index for active users
    __table_args__ = (
        Index('idx_user_active_email', 'is_active', 'email'),
    )

class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    filename = Column(String, nullable=False)
    narrative = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Add composite indexes for common queries
    __table_args__ = (
        Index('idx_image_user_created', 'user_id', 'created_at'),
        Index('idx_image_active', 'is_deleted', 'created_at'),
    )
