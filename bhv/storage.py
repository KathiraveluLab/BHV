import os
import uuid
import logging
from PIL import Image as PILImage
from fastapi import UploadFile
from bhv.validation import validate_filename, validate_file_size

logger = logging.getLogger(__name__)

# Image processing constants
THUMBNAIL_SIZE = (300, 300)
IMAGE_QUALITY = 85
MAX_IMAGE_DIMENSION = 4096

def _secure_name(name):
    """Generate secure filename with UUID."""
    uid = uuid.uuid4().hex
    base, ext = os.path.splitext(name)
    if not ext:
        ext = '.jpg'
    return f"{uid}{ext}"

async def _read_file_async(file):
    """Read file content asynchronously."""
    return await file.read()

def _optimize_image(path: str, thumb_path: str):
    """Optimize and create thumbnail for image."""
    try:
        img = PILImage.open(path)
        
        # Validate image dimensions
        width, height = img.size
        if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
            logger.warning(f"Image dimensions too large: {width}x{height}")
            # Resize to fit
            img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), PILImage.Resampling.LANCZOS)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            bg = PILImage.new('RGB', img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = bg
        
        # Save main image with compression
        img.save(path, 'JPEG', quality=IMAGE_QUALITY, optimize=True)
        
        # Create thumbnail
        img.thumbnail(THUMBNAIL_SIZE, PILImage.Resampling.LANCZOS)
        img.save(thumb_path, 'JPEG', quality=IMAGE_QUALITY, optimize=True)
        
        logger.info(f"Image optimized: {path}")
        return True
    except (IOError, OSError, PILImage.UnidentifiedImageError) as e:
        logger.warning(f"Failed to process image: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while processing image: {e}")
        return False

def save_upload(upload: UploadFile):
    """Save uploaded file with validation and optimization."""
    # Validate filename
    is_valid, error = validate_filename(upload.filename)
    if not is_valid:
        raise ValueError(f"Invalid file: {error}")
    
    fname = _secure_name(upload.filename)
    path = os.path.join('data', 'images', fname)
    
    try:
        # Read and save file
        content = upload.file.read()
        
        # Validate file size
        is_valid, error = validate_file_size(len(content))
        if not is_valid:
            raise ValueError(f"Invalid file: {error}")
        
        with open(path, 'wb') as f:
            f.write(content)
        
        # Optimize and create thumbnail
        thumb_path = os.path.join('data', 'images', f'thumb-{fname}')
        _optimize_image(path, thumb_path)
        
        logger.info(f"File uploaded successfully: {fname}")
        return fname
    except ValueError as e:
        logger.warning(f"Upload validation failed: {e}")
        # Clean up partial file
        if os.path.exists(path):
            os.remove(path)
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        # Clean up partial file
        if os.path.exists(path):
            os.remove(path)
        raise

def delete_image(filename: str):
    """Delete image and thumbnail."""
    try:
        path = os.path.join('data', 'images', filename)
        thumb_path = os.path.join('data', 'images', f'thumb-{filename}')
        
        if os.path.exists(path):
            os.remove(path)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        
        logger.info(f"Image deleted: {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete image {filename}: {e}")
        return False
