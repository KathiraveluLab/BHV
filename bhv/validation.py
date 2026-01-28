"""Security and validation utilities for BHV."""
import re
from typing import Optional, Tuple
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Constants
MAX_EMAIL_LENGTH = 255
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 256
MAX_NARRATIVE_LENGTH = 10000
MAX_FILENAME_LENGTH = 255
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or len(email) > MAX_EMAIL_LENGTH:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength."""
    if not password:
        return False, "Password is required"
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password must be less than {MAX_PASSWORD_LENGTH} characters"
    
    # Check for at least one uppercase, one lowercase, one digit
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and digits"
    
    return True, ""


def validate_narrative(narrative: Optional[str]) -> bool:
    """Validate narrative text."""
    if narrative is None:
        return True
    return len(narrative) <= MAX_NARRATIVE_LENGTH


def validate_filename(filename: str) -> Tuple[bool, str]:
    """Validate filename."""
    if not filename or len(filename) > MAX_FILENAME_LENGTH:
        return False, "Invalid filename length"
    
    # Check extension
    ext = filename[filename.rfind('.'):].lower()
    if ext.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        return False, f"File extension {ext} not allowed"
    
    return True, ""


def validate_file_size(file_size: int) -> Tuple[bool, str]:
    """Validate file size."""
    if file_size <= 0:
        return False, "File is empty"
    if file_size > MAX_FILE_SIZE:
        return False, f"File exceeds maximum size of {MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
    
    return True, ""


class ValidationError(Exception):
    """Custom validation error."""
    pass
