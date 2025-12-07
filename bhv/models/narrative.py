"""Narrative model for patient stories."""
from bhv.database import db
from datetime import datetime

class Narrative(db.Model):
    __tablename__ = 'narratives'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to user who created the narrative
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_narratives')
    
    def __repr__(self):
        return f'<Narrative {self.id} for Image {self.image_id}>'
    
    def to_dict(self):
        """Convert narrative to dictionary."""
        return {
            'id': self.id,
            'image_id': self.image_id,
            'content': self.content,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'last_modified': self.last_modified.isoformat()
        }