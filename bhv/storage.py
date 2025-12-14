import os
import uuid
from PIL import Image as PILImage
import aiofiles

def _secure_name(name):
    uid = uuid.uuid4().hex
    base, ext = os.path.splitext(name)
    if not ext:
        ext = '.jpg'
    return f"{uid}{ext}"

def save_upload(upload):
    fname = _secure_name(upload.filename)
    path = os.path.join('data', 'images', fname)
    with open(path, 'wb') as f:
        shutil = upload.file.read()
        f.write(shutil)
    try:
        img = PILImage.open(path)
        img.thumbnail((300, 300))
        thumb = os.path.join('data', 'images', f'thumb-{fname}')
        img.save(thumb)
    except Exception:
        pass
    return fname
