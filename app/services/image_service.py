import os
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import BASE_DIR, IMAGE_STORAGE_DIR


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf"}
SENTIMENT_OPTIONS = {"positive", "neutral", "negative"}


def is_allowed_image(filename: str) -> bool:
    extension = Path(filename).suffix.lower()
    return extension in ALLOWED_EXTENSIONS


def save_image_file(upload_file: UploadFile, user_id: str) -> str:
    user_folder = IMAGE_STORAGE_DIR / user_id
    user_folder.mkdir(parents=True, exist_ok=True)

    extension = Path(upload_file.filename or "").suffix.lower()
    extension = extension if extension in ALLOWED_EXTENSIONS else ".jpg"
    new_filename = f"{uuid4().hex}{extension}"
    destination = user_folder / new_filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    relative_path = os.path.join("storage", "images", user_id, new_filename)
    return relative_path


def delete_image_file(image_path: str) -> None:
    if not image_path:
        return

    image_full_path = (BASE_DIR / image_path).resolve()

    # Prevent path traversal attacks by ensuring the path is within the storage directory.
    if not str(image_full_path).startswith(str(IMAGE_STORAGE_DIR.resolve())):
        return

    if image_full_path.is_file():
        image_full_path.unlink()


def is_valid_sentiment(sentiment: str) -> bool:
    return sentiment.lower() in SENTIMENT_OPTIONS
