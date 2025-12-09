"""Password hashing and validation for secure authentication."""
import bcrypt


class PasswordManager:
    """Handles secure password operations using bcrypt."""
    
    MIN_LENGTH = 8
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with cost factor 12."""
        if not password:
            raise ValueError("Password cannot be empty")
        
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against stored hash."""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple:
        """Validate password meets security requirements."""
        if len(password) < PasswordManager.MIN_LENGTH:
            return False, f"Password must be at least {PasswordManager.MIN_LENGTH} characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if not any(c in PasswordManager.SPECIAL_CHARS for c in password):
            return False, "Password must contain at least one special character"
        
        return True, None
    
    @staticmethod
    def generate_password_requirements_text() -> str:
        """Generate human-readable password requirements text."""
        return f"""Password must:
- Be at least {PasswordManager.MIN_LENGTH} characters long
- Contain uppercase and lowercase letters
- Contain at least one digit
- Contain at least one special character ({PasswordManager.SPECIAL_CHARS[:20]}...)"""