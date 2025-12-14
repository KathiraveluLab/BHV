from fastapi import Request, Depends, HTTPException
from passlib.hash import bcrypt
from bhv.models import User
from bhv.db import SessionLocal

def create_user(db, email, password):
    h = bcrypt.hash(password)
    u = User(email=email, password_hash=h)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def authenticate_user(db, email, password):
    u = db.query(User).filter(User.email == email).first()
    if not u:
        return None
    if not bcrypt.verify(password, u.password_hash):
        return None
    return u

def require_user(request: Request):
    u = request.session.get('user')
    if not u:
        raise HTTPException(status_code=303, detail='login required')
    return u

def logout_user(request: Request):
    request.session.pop('user', None)
