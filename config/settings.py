"""
Configuration management for BHV application.

This module handles all configuration settings including environment variables,
database paths, security settings, and server configuration.
"""

import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """
    Central configuration management class for BHV application.
    
    Handles loading configuration from environment variables with sensible defaults
    for development and production environments.
    """
    
    def __init__(self):
        """Initialize configuration with environment variables and defaults."""
        self.base_dir = Path(__file__).parent.parent
        self._load_environment()
    
    def _load_environment(self):
        """Load configuration from environment variables with defaults."""
        # Security Configuration
        self.SECRET_KEY = os.getenv('SECRET_KEY', self._generate_secret_key())
        
        # Database Configuration
        self.DATABASE_PATH = os.getenv('DATABASE_PATH', str(self.base_dir / 'data' / 'bhv.db'))
        
        # File Storage Configuration
        self.UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(self.base_dir / 'media' / 'uploads'))
        self.MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
        
        # Server Configuration
        self.HOST = os.getenv('HOST', '127.0.0.1')
        self.PORT = int(os.getenv('PORT', 5000))
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Security Settings
        self.SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 1 hour
        self.ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif,bmp,tiff').split(','))
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', str(self.base_dir / 'logs' / 'bhv.log'))
        
        # Healthcare Compliance
        self.AUDIT_ENABLED = os.getenv('AUDIT_ENABLED', 'True').lower() == 'true'
        self.DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', 2555))  # 7 years default
        
        # Ensure required directories exist
        self._create_directories()
    
    def _generate_secret_key(self) -> str:
        """
        Generate a secure secret key if not provided in environment.
        
        Returns:
            str: Generated secret key
        """
        import secrets
        return secrets.token_hex(32)
    
    def _create_directories(self):
        """Create required directories if they don't exist."""
        directories = [
            Path(self.DATABASE_PATH).parent,
            Path(self.UPLOAD_FOLDER),
            Path(self.LOG_FILE).parent
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_flask_config(self) -> Dict[str, Any]:
        """
        Get Flask-specific configuration dictionary.
        
        Returns:
            Dict[str, Any]: Flask configuration settings
        """
        return {
            'SECRET_KEY': self.SECRET_KEY,
            'UPLOAD_FOLDER': self.UPLOAD_FOLDER,
            'MAX_CONTENT_LENGTH': self.MAX_CONTENT_LENGTH,
            'SESSION_PERMANENT': False,
            'PERMANENT_SESSION_LIFETIME': self.SESSION_TIMEOUT
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """
        Get database configuration dictionary.
        
        Returns:
            Dict[str, Any]: Database configuration settings
        """
        return {
            'database_path': self.DATABASE_PATH,
            'audit_enabled': self.AUDIT_ENABLED,
            'retention_days': self.DATA_RETENTION_DAYS
        }
    
    def get_server_config(self) -> Dict[str, Any]:
        """
        Get server configuration dictionary.
        
        Returns:
            Dict[str, Any]: Server configuration settings
        """
        return {
            'host': self.HOST,
            'port': self.PORT,
            'debug': self.DEBUG
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """
        Get security configuration dictionary.
        
        Returns:
            Dict[str, Any]: Security configuration settings
        """
        return {
            'allowed_extensions': self.ALLOWED_EXTENSIONS,
            'max_file_size': self.MAX_CONTENT_LENGTH,
            'session_timeout': self.SESSION_TIMEOUT,
            'audit_enabled': self.AUDIT_ENABLED
        }
    
    def validate_config(self) -> Dict[str, bool]:
        """
        Validate current configuration settings.
        
        Returns:
            Dict[str, bool]: Validation results for each configuration area
        """
        results = {}
        
        # Check database directory
        results['database_accessible'] = Path(self.DATABASE_PATH).parent.exists()
        
        # Check upload directory
        results['upload_directory_writable'] = os.access(self.UPLOAD_FOLDER, os.W_OK)
        
        # Check log directory
        results['log_directory_writable'] = os.access(Path(self.LOG_FILE).parent, os.W_OK)
        
        # Check secret key strength
        results['secret_key_secure'] = len(self.SECRET_KEY) >= 32
        
        # Check port availability (basic check)
        results['port_valid'] = 1024 <= self.PORT <= 65535
        
        return results
    
    def __str__(self) -> str:
        """
        String representation of configuration (excluding sensitive data).
        
        Returns:
            str: Configuration summary
        """
        return f"""BHV Configuration:
  Database: {self.DATABASE_PATH}
  Upload Folder: {self.UPLOAD_FOLDER}
  Server: {self.HOST}:{self.PORT}
  Debug: {self.DEBUG}
  Audit: {self.AUDIT_ENABLED}
  Max File Size: {self.MAX_CONTENT_LENGTH / (1024*1024):.1f}MB
  Allowed Extensions: {', '.join(self.ALLOWED_EXTENSIONS)}"""