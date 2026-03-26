import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.db import get_db
from app.models.user import User
from app.routes.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])
UPLOAD_DIR = "uploads"

class UserUpdate(BaseModel):
    full_name: str = None
    is_active: bool = None
    is_admin: bool = None

def get_admin_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    """Verify user is admin via JWT token."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.get("/users")
def get_all_users(admin=Depends(get_admin_user), db: Session = Depends(get_db)):
    """Admin: Get all users."""
    users = db.query(User).all()
    return {"total": len(users), "users": [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "is_admin": u.is_admin,
            "is_active": u.is_active
        } for u in users
    ]}

@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    update: UserUpdate,
    admin=Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Admin: Update user details."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if update.full_name is not None:
        user.full_name = update.full_name
    if update.is_active is not None:
        user.is_active = update.is_active
    if update.is_admin is not None:
        user.is_admin = update.is_admin
    db.commit()
    db.refresh(user)
    return {"message": "User updated", "user": {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_admin": user.is_admin,
        "is_active": user.is_active
    }}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin=Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Admin: Delete user and their images."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_dir = os.path.join(UPLOAD_DIR, str(user_id))
    if os.path.exists(user_dir):
        shutil.rmtree(user_dir)
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}

@router.get("/stats")
def get_stats(admin=Depends(get_admin_user), db: Session = Depends(get_db)):
    """Admin: Get system statistics."""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_images = 0
    if os.path.exists(UPLOAD_DIR):
        for user_dir in os.listdir(UPLOAD_DIR):
            user_path = os.path.join(UPLOAD_DIR, user_dir)
            if os.path.isdir(user_path):
                total_images += len(os.listdir(user_path))
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_images": total_images
    }