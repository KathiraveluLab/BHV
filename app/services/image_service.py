import uuid, json, shutil
from pathlib import Path
from fuzzy_emotion import detect_fuzzy_emotion

UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_image(db, user, image, visibility):
    ext = Path(image.filename).suffix or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    path = UPLOAD_DIR / filename

    with open(path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    metadata = detect_fuzzy_emotion(str(path))

    db.execute(
        "INSERT INTO images (user_name, filename, metadata, visibility) VALUES (?, ?, ?, ?)",
        (user, filename, json.dumps(metadata), visibility)
    )
    db.commit()


def delete_image(db, user, filename):
    safe_name = Path(filename).name
    file_path = UPLOAD_DIR / safe_name

    db.execute(
        "DELETE FROM images WHERE filename=? AND user_name=?",
        (safe_name, user)
    )
    db.commit()

    if file_path.exists():
        file_path.unlink()
