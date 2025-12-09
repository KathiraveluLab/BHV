"""Tests for security module."""
import pytest
from bhv.security.password import PasswordManager
from bhv.security.validators import Validator


class TestPasswordManager:
    """Test password hashing and validation."""
    
    def test_password_hashing(self):
        """Test password hashing produces different hashes."""
        password = "SecurePass123!"
        hash1 = PasswordManager.hash_password(password)
        hash2 = PasswordManager.hash_password(password)
        
        assert hash1 != hash2
        assert hash1 != password
        assert len(hash1) == 60
    
    def test_password_verification(self):
        """Test password verification works correctly."""
        password = "SecurePass123!"
        hashed = PasswordManager.hash_password(password)
        
        assert PasswordManager.verify_password(password, hashed) is True
        assert PasswordManager.verify_password("WrongPassword", hashed) is False
    
    def test_empty_password(self):
        """Test that empty password raises error."""
        with pytest.raises(ValueError):
            PasswordManager.hash_password("")
    
    def test_password_strength_valid(self):
        """Test valid passwords pass strength check."""
        valid_passwords = [
            "SecurePass123!",
            "MyP@ssw0rd",
            "Complex!Pass123"
        ]
        
        for pwd in valid_passwords:
            valid, msg = PasswordManager.validate_password_strength(pwd)
            assert valid is True
            assert msg is None
    
    def test_password_strength_too_short(self):
        """Test password too short fails."""
        valid, msg = PasswordManager.validate_password_strength("Short1!")
        assert valid is False
        assert "8 characters" in msg
    
    def test_password_strength_no_uppercase(self):
        """Test password without uppercase fails."""
        valid, msg = PasswordManager.validate_password_strength("securepass123!")
        assert valid is False
        assert "uppercase" in msg
    
    def test_password_strength_no_lowercase(self):
        """Test password without lowercase fails."""
        valid, msg = PasswordManager.validate_password_strength("SECUREPASS123!")
        assert valid is False
        assert "lowercase" in msg
    
    def test_password_strength_no_digit(self):
        """Test password without digit fails."""
        valid, msg = PasswordManager.validate_password_strength("SecurePass!")
        assert valid is False
        assert "digit" in msg
    
    def test_password_strength_no_special(self):
        """Test password without special character fails."""
        valid, msg = PasswordManager.validate_password_strength("SecurePass123")
        assert valid is False
        assert "special character" in msg
    
    def test_password_requirements_text(self):
        """Test password requirements text generation."""
        text = PasswordManager.generate_password_requirements_text()
        assert "8 characters" in text
        assert "uppercase" in text
        assert "lowercase" in text


class TestValidator:
    """Test input validation."""
    
    def test_email_validation_valid(self):
        """Test valid emails pass validation."""
        valid_emails = [
            "user@example.com",
            "john.doe@example.co.uk",
            "test+tag@domain.org"
        ]
        
        for email in valid_emails:
            assert Validator.validate_email(email) is True
    
    def test_email_validation_invalid(self):
        """Test invalid emails fail validation."""
        invalid_emails = [
            "invalid.email",
            "@example.com",
            "user@",
            "",
            "user@.com"
        ]
        
        for email in invalid_emails:
            assert Validator.validate_email(email) is False
    
    def test_email_validation_none(self):
        """Test None email fails validation."""
        assert Validator.validate_email(None) is False
    
    def test_narrative_sanitization(self):
        """Test narrative sanitization removes XSS."""
        dirty = "<script>alert('xss')</script>Hello World"
        clean = Validator.sanitize_narrative(dirty)
        assert "<script>" not in clean
        assert "Hello World" in clean
    
    def test_narrative_length_limit(self):
        """Test narrative length is limited."""
        long_text = "a" * 10000
        clean = Validator.sanitize_narrative(long_text)
        assert len(clean) <= Validator.MAX_NARRATIVE_LENGTH
    
    def test_narrative_whitespace_cleaning(self):
        """Test excessive whitespace is cleaned."""
        dirty = "Hello     World    Test"
        clean = Validator.sanitize_narrative(dirty)
        assert clean == "Hello World Test"
    
    def test_username_validation_valid(self):
        """Test valid usernames pass."""
        valid_usernames = ["john_doe", "user123", "test-user", "abc"]
        
        for username in valid_usernames:
            valid, msg = Validator.validate_username(username)
            assert valid is True
    
    def test_username_validation_too_short(self):
        """Test username too short fails."""
        valid, msg = Validator.validate_username("ab")
        assert valid is False
        assert "3-50 characters" in msg
    
    def test_username_validation_invalid_start(self):
        """Test username must start with letter."""
        valid, msg = Validator.validate_username("123user")
        assert valid is False
        assert "start with a letter" in msg
    
    def test_filename_sanitization(self):
        """Test filename sanitization."""
        clean = Validator.sanitize_filename("../../etc/passwd")
        assert ".." not in clean
        assert "/" not in clean
    
    def test_image_validation_no_file(self):
        """Test validation fails when no file provided."""
        valid, msg = Validator.validate_image_upload(None)
        assert valid is False
        assert "No file" in msg