"""
Simple unit tests for validation functions
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bhv.app import (
    allowed_file, sanitize_filename, generate_unique_filename,
    validate_file_size
)

def test_allowed_file_valid():
    """Test valid file extensions"""
    allowed = {'jpg', 'png', 'gif'}
    assert allowed_file('test.jpg', allowed) == True
    assert allowed_file('test.PNG', allowed) == True

def test_allowed_file_invalid():
    """Test invalid file extensions"""
    allowed = {'jpg', 'png', 'gif'}
    assert allowed_file('test.exe', allowed) == False
    assert allowed_file('test.php', allowed) == False

def test_sanitize_filename():
    """Test filename sanitization"""
    result = sanitize_filename('test.jpg')
    assert result == 'test.jpg'
    
    # Path traversal should be removed
    result = sanitize_filename('../../../etc/passwd')
    assert '../' not in result

def test_generate_unique_filename():
    """Test unique filename generation"""
    name1 = generate_unique_filename('test.jpg')
    name2 = generate_unique_filename('test.jpg')
    
    # Should be different
    assert name1 != name2
    # Should keep extension
    assert name1.endswith('.jpg')

def test_validate_file_size():
    """Test file size validation"""
    max_size = 5 * 1024 * 1024
    
    assert validate_file_size(1024, max_size) == True
    assert validate_file_size(0, max_size) == False
    assert validate_file_size(max_size + 1, max_size) == False