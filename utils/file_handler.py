"""
File handling utilities for BHV application.

This module provides secure file upload, storage, and retrieval functionality
for patient-provided images with proper validation and organization.
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import mimetypes
import hashlib

from config.settings import Config


class FileHandler:
    """
    Secure file handling for image uploads and storage.
    
    Provides methods for validating, saving, and organizing uploaded files
    with proper security measures and healthcare compliance.
    """
    
    def __init__(self, upload_folder: str):
        """
        Initialize file handler with upload directory.
        
        Args:
            upload_folder (str): Base directory for file uploads
        """
        self.upload_folder = Path(upload_folder)
        self.config = Config()
        self.security_config = self.config.get_security_config()
        
        # Ensure upload directory exists
        self.upload_folder.mkdir(parents=True, exist_ok=True)
    
    def allowed_file(self, filename: str) -> bool:
        """
        Check if file extension is allowed.
        
        Args:
            filename (str): Name of the file to check
            
        Returns:
            bool: True if file extension is allowed
        """
        if not filename or '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self.security_config['allowed_extensions']
    
    def validate_file(self, file: FileStorage) -> Tuple[bool, str]:
        """
        Comprehensive file validation including size, type, and content.
        
        Args:
            file (FileStorage): Uploaded file object
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Check if file exists
        if not file or not file.filename:
            return False, "No file provided"
        
        # Check file extension
        if not self.allowed_file(file.filename):
            allowed = ', '.join(self.security_config['allowed_extensions'])
            return False, f"File type not allowed. Allowed types: {allowed}"
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > self.security_config['max_file_size']:
            max_size_mb = self.security_config['max_file_size'] / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_size_mb:.1f}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Validate MIME type
        mime_type, _ = mimetypes.guess_type(file.filename)
        if not mime_type or not mime_type.startswith('image/'):
            return False, "File is not a valid image"
        
        return True, "File is valid"
    
    def generate_unique_filename(self, original_filename: str, user_id: int) -> str:
        """
        Generate a unique filename to prevent conflicts and enhance security.
        
        Args:
            original_filename (str): Original filename from upload
            user_id (int): ID of the user uploading the file
            
        Returns:
            str: Unique filename with timestamp and UUID
        """
        # Secure the original filename
        secure_name = secure_filename(original_filename)
        
        # Extract extension
        name, ext = os.path.splitext(secure_name)
        
        # Generate unique identifier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        # Create new filename: user_timestamp_uuid_originalname.ext
        new_filename = f"user{user_id}_{timestamp}_{unique_id}_{name}{ext}"
        
        return new_filename
    
    def get_user_directory(self, user_id: int) -> Path:
        """
        Get or create user-specific upload directory.
        
        Args:
            user_id (int): User ID
            
        Returns:
            Path: Path to user's upload directory
        """
        user_dir = self.upload_folder / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def save_file(self, file: FileStorage, user_id: int) -> str:
        """
        Save uploaded file with proper validation and organization.
        
        Args:
            file (FileStorage): Uploaded file object
            user_id (int): ID of the user uploading the file
            
        Returns:
            str: Relative path to saved file
            
        Raises:
            ValueError: If file validation fails
            IOError: If file save operation fails
        """
        # Validate file
        is_valid, error_message = self.validate_file(file)
        if not is_valid:
            raise ValueError(error_message)
        
        # Generate unique filename
        unique_filename = self.generate_unique_filename(file.filename, user_id)
        
        # Get user directory
        user_dir = self.get_user_directory(user_id)
        
        # Create date-based subdirectory
        date_dir = user_dir / datetime.now().strftime('%Y/%m')
        date_dir.mkdir(parents=True, exist_ok=True)
        
        # Full file path
        file_path = date_dir / unique_filename
        
        try:
            # Save file
            file.save(str(file_path))
            
            # Return relative path from upload folder
            relative_path = file_path.relative_to(self.upload_folder)
            return str(relative_path)
            
        except Exception as e:
            raise IOError(f"Failed to save file: {str(e)}")
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get detailed information about a stored file.
        
        Args:
            file_path (str): Relative path to the file
            
        Returns:
            dict: File information including size, type, and metadata
        """
        full_path = self.upload_folder / file_path
        
        if not full_path.exists():
            return {'exists': False}
        
        stat = full_path.stat()
        mime_type, _ = mimetypes.guess_type(str(full_path))
        
        return {
            'exists': True,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'mime_type': mime_type,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'filename': full_path.name,
            'extension': full_path.suffix.lower()
        }
    
    def delete_file(self, file_path: str) -> bool:
        """
        Safely delete a file from storage.
        
        Args:
            file_path (str): Relative path to the file
            
        Returns:
            bool: True if file was deleted successfully
        """
        full_path = self.upload_folder / file_path
        
        try:
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_user_files(self, user_id: int) -> List[dict]:
        """
        Get list of all files for a specific user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            List[dict]: List of file information dictionaries
        """
        user_dir = self.upload_folder / f"user_{user_id}"
        
        if not user_dir.exists():
            return []
        
        files = []
        for file_path in user_dir.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.upload_folder)
                file_info = self.get_file_info(str(relative_path))
                file_info['relative_path'] = str(relative_path)
                files.append(file_info)
        
        # Sort by creation time, newest first
        files.sort(key=lambda x: x.get('created', datetime.min), reverse=True)
        return files
    
    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """
        Calculate SHA-256 hash of a file for integrity verification.
        
        Args:
            file_path (str): Relative path to the file
            
        Returns:
            Optional[str]: SHA-256 hash or None if file doesn't exist
        """
        full_path = self.upload_folder / file_path
        
        if not full_path.exists():
            return None
        
        sha256_hash = hashlib.sha256()
        
        try:
            with open(full_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception:
            return None
    
    def get_storage_stats(self) -> dict:
        """
        Get storage statistics for the entire upload directory.
        
        Returns:
            dict: Storage statistics including total size and file counts
        """
        stats = {
            'total_files': 0,
            'total_size': 0,
            'total_size_mb': 0,
            'users_with_files': 0,
            'file_types': {}
        }
        
        user_dirs = set()
        
        for file_path in self.upload_folder.rglob('*'):
            if file_path.is_file():
                stats['total_files'] += 1
                file_size = file_path.stat().st_size
                stats['total_size'] += file_size
                
                # Track file types
                extension = file_path.suffix.lower()
                stats['file_types'][extension] = stats['file_types'].get(extension, 0) + 1
                
                # Track users with files
                if 'user_' in str(file_path):
                    user_dir = str(file_path).split('user_')[1].split('/')[0].split('\\')[0]
                    user_dirs.add(user_dir)
        
        stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)
        stats['users_with_files'] = len(user_dirs)
        
        return stats
    
    def cleanup_empty_directories(self):
        """Remove empty directories from the upload folder."""
        for root, dirs, files in os.walk(self.upload_folder, topdown=False):
            for directory in dirs:
                dir_path = Path(root) / directory
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                except OSError:
                    pass  # Directory not empty or permission issue


class ImageProcessor:
    """
    Image processing utilities for thumbnails and metadata extraction.
    
    Optional component for advanced image handling (requires PIL/Pillow).
    """
    
    def __init__(self):
        """Initialize image processor."""
        self.thumbnail_size = (200, 200)
        
        try:
            from PIL import Image
            self.pil_available = True
        except ImportError:
            self.pil_available = False
    
    def create_thumbnail(self, file_path: str, thumbnail_path: str) -> bool:
        """
        Create thumbnail for an image file.
        
        Args:
            file_path (str): Path to original image
            thumbnail_path (str): Path for thumbnail
            
        Returns:
            bool: True if thumbnail created successfully
        """
        if not self.pil_available:
            return False
        
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                img.save(thumbnail_path, optimize=True, quality=85)
            return True
        except Exception:
            return False
    
    def get_image_metadata(self, file_path: str) -> dict:
        """
        Extract metadata from image file.
        
        Args:
            file_path (str): Path to image file
            
        Returns:
            dict: Image metadata
        """
        metadata = {'has_metadata': False}
        
        if not self.pil_available:
            return metadata
        
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            with Image.open(file_path) as img:
                metadata.update({
                    'has_metadata': True,
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height
                })
                
                # Extract EXIF data if available
                exif_data = img.getexif()
                if exif_data:
                    exif = {}
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif[tag] = value
                    metadata['exif'] = exif
                    
        except Exception:
            pass
        
        return metadata