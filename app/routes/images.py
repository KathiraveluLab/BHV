import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.db import get_db
from app.models.user import User

router = APIRouter(prefix="/images", tags=["Images"])

UPLOAD_DIR = "uploads"
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_SIZE = 5 * 1024 * 1024  # 5MB

os.makedirs(UPLOAD_DIR, exist_ok=True)


class ImageResponse(BaseModel):
    id: str
    filename: str
    filepath: str
    message: str


@router.post("/upload", response_model=ImageResponse)
async def upload_image(
    user_id: int,
    narrative: str = "",
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an image with optional narrative for a user."""

    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {ALLOWED_TYPES}"
        )

    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB"
        )

    # Save file with unique name
    file_id = str(uuid.uuid4())
    _, ext = os.path.splitext(file.filename)
    filename = f"{file_id}{ext}"

    filepath = os.path.join(UPLOAD_DIR, str(user_id), filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "wb") as f:
        f.write(content)

    return ImageResponse(
        id=file_id,
        filename=filename,
        filepath=filepath,
        message="Image uploaded successfully"
    )


@router.get("/user/{user_id}")
def get_user_images(user_id: int, db: Session = Depends(get_db)):
    """Get all images for a user."""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_upload_dir = os.path.join(UPLOAD_DIR, str(user_id))

    if not os.path.exists(user_upload_dir):
        return {"user_id": user_id, "images": []}

    images = []
    for filename in os.listdir(user_upload_dir):
        filepath = os.path.join(user_upload_dir, filename)

        images.append({
            "filename": filename,
            "filepath": filepath,
            "size": os.path.getsize(filepath)
        })

    return {"user_id": user_id, "images": images}


@router.delete("/user/{user_id}/{filename}")
def delete_image(user_id: int, filename: str, db: Session = Depends(get_db)):
    """Delete an image for a user."""

    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    filepath = os.path.join(UPLOAD_DIR, str(user_id), filename)

    # Prevent path traversal attack
    user_dir_abs = os.path.abspath(os.path.join(UPLOAD_DIR, str(user_id)))
    filepath_abs = os.path.abspath(filepath)

    if not filepath_abs.startswith(user_dir_abs):
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")

    os.remove(filepath)

    return {"message": f"Image {filename} deleted successfully"}