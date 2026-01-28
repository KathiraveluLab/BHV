from fastapi import Request, Depends, HTTPException
from passlib.hash import bcrypt
from bhv.models import User
from bhv.db import SessionLocal
from bhv.validation import validate_email, validate_password
import logging

logger = logging.getLogger(__name__)

def create_user(db, email, password):
    """Create new user with validation."""
    if not validate_email(email):
        raise ValueError("Invalid email format")
    
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        raise ValueError(error_msg)
    
    h = bcrypt.hash(password)
    u = User(email=email, password_hash=h, is_active=True)
    db.add(u)
    db.commit()
    db.refresh(u)
    logger.info(f"User created: {email}")
    return u

def authenticate_user(db, email, password):
    """Authenticate user with rate limiting consideration."""
    if not validate_email(email):
        return None
    
    u = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not u:
        logger.warning(f"Authentication attempt for non-existent user: {email}")
        return None
    if not bcrypt.verify(password, u.password_hash):
        logger.warning(f"Failed authentication for user: {email}")
        return None
    
    logger.info(f"User authenticated: {email}")
    return u

def require_user(request: Request):
    """Require authenticated user."""
    u = request.session.get('user')
    if not u:
        raise HTTPException(status_code=401, detail='Not authenticated')
    return u

def logout_user(request: Request):
    """Logout user and clear session."""
    user_email = request.session.get('user', {}).get('email', 'unknown')
    request.session.pop('user', None)
    logger.info(f"User logged out: {user_email}")
