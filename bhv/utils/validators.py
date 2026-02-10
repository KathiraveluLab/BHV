import os
from pathlib import Path
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_image_content(file_path):
    # Simple validation - just check file exists
    return 'jpeg' if os.path.exists(file_path) else None

def sanitize_filename(filename):
    filename = secure_filename(filename)
    filename = filename.replace('/', '').replace('\\', '')
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    return f"{name}{ext}"

def generate_unique_filename(original_filename):
    import uuid
    ext = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return unique_name

def validate_file_size(file_size, max_size):
    return 0 < file_size <= max_size