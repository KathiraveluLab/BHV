"""Configuration settings for the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, override=True)


def get_admin_emails():
    """
    Get admin emails list from environment.
    Reloads .env file to ensure latest values are used.
    Returns empty list if not set.
    Supports comma-separated emails: ADMIN_EMAILS=admin1@example.com,admin2@example.com
    """
    # Reload .env file to get latest values
    load_dotenv(dotenv_path=env_path, override=True)
    
    admin_emails_str = os.environ.get('ADMIN_EMAILS', '').strip()
    if not admin_emails_str:
        # Also check ADMIN_EMAIL (singular) for backwards compatibility
        admin_email = os.environ.get('ADMIN_EMAIL', '').strip()
        if admin_email:
            return [admin_email.lower()]
        return []
    
    # Parse comma-separated list, removing empty strings and normalizing
    emails = []
    for email in admin_emails_str.split(','):
        email = email.strip()
        if email:  # Only add non-empty emails
            emails.append(email.lower())
    
    return emails


def is_admin_email(email):
    """
    Check if an email is in the admin emails list in .env file.
    Always checks fresh from environment variables.
    Case-insensitive comparison.
    Supports multiple admin emails via ADMIN_EMAILS (comma-separated).
    """
    if not email:
        return False
    
    # Normalize email
    email_normalized = email.strip().lower()
    if not email_normalized:
        return False
    
    # Get admin emails list (fresh from .env)
    admin_emails = get_admin_emails()
    if not admin_emails:
        return False
    
    return email_normalized in admin_emails


# Store reference to module-level function for Config class to use
_module_is_admin_email = is_admin_email


class Config:
    """Base configuration class."""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MongoDB settings
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/bhv'
    MONGODB_DB = os.environ.get('MONGODB_DB') or 'bhv'
    
    # Flask-Mail settings
    MAIL_SERVER = (os.environ.get('MAIL_SERVER') or 'smtp.gmail.com').strip()
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    
    # Strip whitespace and quotes from credentials to avoid issues
    def clean_env_value(value):
        """Clean environment variable value by removing quotes and whitespace."""
        if not value:
            return None
        value = value.strip()
        # Remove surrounding quotes if present
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1].strip()
        return value if value else None
    
    MAIL_USERNAME = clean_env_value(os.environ.get('MAIL_USERNAME'))
    MAIL_PASSWORD = clean_env_value(os.environ.get('MAIL_PASSWORD'))
    MAIL_DEFAULT_SENDER = clean_env_value(os.environ.get('MAIL_DEFAULT_SENDER')) or MAIL_USERNAME
    
    # Additional Flask-Mail settings
    MAIL_USE_SSL = False
    MAIL_DEBUG = False
    
    # OAuth settings
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # OTP settings
    OTP_EXPIRY_MINUTES = int(os.environ.get('OTP_EXPIRY_MINUTES') or 10)
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'wav', 'mp3', 'm4a', 'ogg'}
    
    # Flask-Login settings
    SESSION_PROTECTION = 'strong'
    
    # Admin settings - use function to get admin emails (always fresh)
    ADMIN_EMAILS = get_admin_emails()  # Initial load for backwards compatibility
    
    @staticmethod
    def is_admin_email(email):
        """Check if an email is in the admin emails list (always checks fresh from .env)."""
        # Call the module-level function to avoid recursion
        return _module_is_admin_email(email)
