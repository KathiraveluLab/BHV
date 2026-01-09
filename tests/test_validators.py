"""
Test suite for BHV validators and helper functions
Tests file validation, sanitization, and security
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bhv.app import allowed_file, sanitize_filename, get_unique_filename


def test_allowed_file_valid_extensions():
    """Test that valid file extensions are accepted"""
    assert allowed_file('image.jpg') == True
    assert allowed_file('photo.jpeg') == True
    assert allowed_file('picture.png') == True
    assert allowed_file('animation.gif') == True
    assert allowed_file('IMAGE.JPG') == True  # Case insensitive


def test_allowed_file_invalid_extensions():
    """Test that invalid file extensions are rejected"""
    assert allowed_file('virus.exe') == False
    assert allowed_file('script.php') == False
    assert allowed_file('hack.sh') == False
    assert allowed_file('document.pdf') == False
    assert allowed_file('code.py') == False


def test_allowed_file_no_extension():
    """Test files without extensions are rejected"""
    assert allowed_file('noextension') == False
    assert allowed_file('file') == False


def test_allowed_file_edge_cases():
    """Test edge cases for file validation"""
    assert allowed_file('') == False
    assert allowed_file('file..jpg') == True


def test_sanitize_filename_basic():
    """Test basic filename sanitization"""
    result = sanitize_filename('test.jpg')
    assert result == 'test.jpg'
    
    # Sanitize converts to lowercase and replaces spaces
    result = sanitize_filename('My Photo.png')
    assert 'photo' in result.lower()
    assert '.png' in result


def test_sanitize_filename_security():
    """Test that path traversal attempts are sanitized"""
    result = sanitize_filename('../../../etc/passwd')
    assert '../' not in result
    
    result = sanitize_filename('..\\..\\windows\\system32')
    assert '\\' not in result


def test_sanitize_filename_special_chars():
    """Test removal of special characters"""
    result = sanitize_filename('file@#$%.jpg')
    # Special chars should be removed or replaced
    assert '.jpg' in result


def test_get_unique_filename_uniqueness():
    """Test that generated filenames are unique"""
    name1 = get_unique_filename('test.jpg')
    name2 = get_unique_filename('test.jpg')
    
    assert name1 != name2
    assert name1.endswith('.jpg')
    assert name2.endswith('.jpg')


def test_get_unique_filename_format():
    """Test that unique filenames have correct format"""
    result = get_unique_filename('photo.png')
    
    # Should contain timestamp and random string
    assert '_' in result
    assert '.png' in result


def test_get_unique_filename_preserves_extension():
    """Test that file extensions are preserved"""
    result = get_unique_filename('image.jpg')
    assert result.endswith('.jpg')
    
    result = get_unique_filename('picture.png')
    assert result.endswith('.png')
    
    result = get_unique_filename('animation.gif')
    assert result.endswith('.gif')