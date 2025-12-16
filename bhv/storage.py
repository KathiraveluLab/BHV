import os
import uuid
import logging
from PIL import Image as PILImage
import aiofiles

logger = logging.getLogger(__name__)

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
    except (IOError, OSError, PILImage.UnidentifiedImageError) as e:
        logger.warning(f"Failed to create thumbnail for {fname}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while processing image {fname}: {e}")
    return fname
