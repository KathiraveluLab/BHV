"""Input validation and sanitization for security."""
import re
import os
from werkzeug.utils import secure_filename


class Validator:
    """Input validation utilities for security."""
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tiff', 'bmp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024
    MAX_NARRATIVE_LENGTH = 5000
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format."""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_image_upload(file) -> tuple:
        """Validate uploaded image file."""
        if not file or not file.filename:
            return False, "No file provided"
        
        filename = secure_filename(file.filename)
        if not filename:
            return False, "Invalid filename"
        
        if '.' not in filename:
            return False, "File must have an extension"
        
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in Validator.ALLOWED_EXTENSIONS:
            allowed = ', '.join(Validator.ALLOWED_EXTENSIONS)
            return False, f"Invalid file type. Allowed: {allowed}"
        
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size == 0:
            return False, "File is empty"
        
        if size > Validator.MAX_FILE_SIZE:
            max_mb = Validator.MAX_FILE_SIZE // (1024 * 1024)
            return False, f"File too large (max {max_mb}MB)"
        
        return True, None
    
    @staticmethod
    def sanitize_narrative(text: str, max_length: int = None) -> str:
        """Sanitize narrative text for safe storage."""
        if not text:
            return ""
        
        if max_length is None:
            max_length = Validator.MAX_NARRATIVE_LENGTH
        
        text = text.replace('\x00', '')
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', text, flags=re.IGNORECASE)
        text = text[:max_length]
        text = ' '.join(text.split())
        
        return text.strip()
    
    @staticmethod
    def validate_username(username: str) -> tuple:
        """Validate username format."""
        if not username:
            return False, "Username is required"
        
        if len(username) < 3 or len(username) > 50:
            return False, "Username must be 3-50 characters long"
        
        pattern = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
        if not re.match(pattern, username):
            return False, "Username must start with a letter and contain only letters, numbers, underscores, and hyphens"
        
        return True, None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage."""
        safe = secure_filename(filename)
        safe = safe.replace(' ', '_')
        safe = re.sub(r'[^a-zA-Z0-9._-]', '', safe)
        return safe