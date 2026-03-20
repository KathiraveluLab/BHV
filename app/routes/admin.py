from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.db import get_db
from app.models.user import User
import os

router = APIRouter(prefix="/admin", tags=["Admin"])

UPLOAD_DIR = "uploads"

class UserUpdate(BaseModel):
    full_name: str = None
    is_active: bool = None
    is_admin: bool = None

@router.get("/users")
def get_all_users(admin_id: int, db: Session = Depends(get_db)):
    """Admin: Get all users."""
    admin = db.query(User).filter(
        User.id == admin_id,
        User.is_admin == True
    ).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")

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
    admin_id: int,
    user_id: int,
    update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Admin: Update user details."""
    admin = db.query(User).filter(
        User.id == admin_id,
        User.is_admin == True
    ).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")

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
    admin_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Admin: Delete user and their images."""
    admin = db.query(User).filter(
        User.id == admin_id,
        User.is_admin == True
    ).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete user images
    user_dir = os.path.join(UPLOAD_DIR, str(user_id))
    if os.path.exists(user_dir):
        for f in os.listdir(user_dir):
            os.remove(os.path.join(user_dir, f))
        os.rmdir(user_dir)

    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}

@router.get("/stats")
def get_stats(admin_id: int, db: Session = Depends(get_db)):
    """Admin: Get system statistics."""
    admin = db.query(User).filter(
        User.id == admin_id,
        User.is_admin == True
    ).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    total_users = db.query(User).count()
    active_users