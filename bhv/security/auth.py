"""Authentication and authorization for BHV."""
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, request, g


class AuthManager:
    """Handles user authentication and session management."""
    
    SESSION_TIMEOUT_HOURS = 24
    
    @staticmethod
    def create_session(user_id: int, remember_me: bool = False):
        """Create user session."""
        session.clear()
        session['user_id'] = user_id
        session['created_at'] = datetime.utcnow().isoformat()
        session['ip_address'] = request.remote_addr
        session.permanent = remember_me
    
    @staticmethod
    def logout_user():
        """Clear user session and log out."""
        session.clear()
    
    @staticmethod
    def get_current_user_id():
        """Get currently logged-in user ID."""
        return session.get('user_id')
    
    @staticmethod
    def validate_session() -> bool:
        """Validate current session is still valid."""
        if 'user_id' not in session:
            return False
        
        created_at_str = session.get('created_at')
        if created_at_str:
            created_at = datetime.fromisoformat(created_at_str)
            age = datetime.utcnow() - created_at