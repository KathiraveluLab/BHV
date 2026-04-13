import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import BASE_DIR, IMAGE_STORAGE_DIR


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf"}
SENTIMENT_OPTIONS = {"positive", "neutral", "negative"}

_JPEG_SIGNATURE = b"\xff\xd8\xff"
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_GIF_SIGNATURES = (b"GIF87a", b"GIF89a")
_PDF_SIGNATURE = b"%PDF-"
_WEBP_SIGNATURE_PREFIX = b"RIFF"
_WEBP_SIGNATURE_SUFFIX = b"WEBP"


def detect_upload_file_extension(upload_file: UploadFile) -> str | None:
    file_obj = upload_file.file
    current_position = file_obj.tell()
    header = file_obj.read(12)
    file_obj.seek(current_position)

    if header.startswith(_JPEG_SIGNATURE):
        return ".jpg"
    if header.startswith(_PNG_SIGNATURE):
        return ".png"
    if header.startswith(_GIF_SIGNATURES):
        return ".gif"
    if header.startswith(_PDF_SIGNATURE):
        return ".pdf"
    if len(header) >= 12 and header.startswith(_WEBP_SIGNATURE_PREFIX) and header[8:12] == _WEBP_SIGNATURE_SUFFIX:
        return ".webp"
    return None


def is_allowed_image(upload_file: UploadFile) -> bool:
    return detect_upload_file_extension(upload_file) is not None


def save_image_file(upload_file: UploadFile, user_id: str, file_extension: str) -> str:
    user_folder = IMAGE_STORAGE_DIR / user_id
    user_folder.mkdir(parents=True, exist_ok=True)

    extension = file_extension.lower()
    if extension not in ALLOWED_EXTENSIONS:
        extension = ".jpg"

    new_filename = f"{uuid4().hex}{extension}"
    destination = user_folder / new_filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    relative_path = (Path("storage") / "images" / user_id / new_filename).as_posix()
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
