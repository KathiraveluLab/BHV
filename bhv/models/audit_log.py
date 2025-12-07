"""Audit log model for HIPAA compliance."""
from bhv.database import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False, index=True)  # 'view', 'edit', 'delete', 'upload'
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    target_image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    ip_address = db.Column(db.String(45))  # Support IPv6
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    details = db.Column(db.Text)  # Additional context as JSON string
    
    # Relationships
    admin = db.relationship('User', foreign_keys=[admin_id], backref='audit_actions')
    target_user = db.relationship('User', foreign_keys=[target_user_id])
    
    def __repr__(self):
        return f'<AuditLog {self.action} by Admin {self.admin_id} at {self.timestamp}>'
    
    def to_dict(self):
        """Convert audit log to dictionary."""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'action': self.action,
            'target_user_id': self.target_user_id,
            'target_image_id': self.target_image_id,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat()
        }