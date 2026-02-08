"""
Authentication and authorization utilities for BHV application.

This module provides secure user authentication, session management,
and role-based access control for healthcare compliance.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from functools import wraps
from flask import session, request, jsonify, redirect, url_for, flash

from models.database import get_db_connection, log_audit_event


class AuthManager:
    """
    Authentication and authorization manager for BHV application.
    
    Handles user authentication, session management, password security,
    and role-based access control with healthcare compliance features.
    """
    
    def __init__(self):
        """Initialize authentication manager."""
        self.session_timeout = 3600  # 1 hour default
        self.max_login_attempts = 5
        self.lockout_duration = 900  # 15 minutes
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Create secure password hash with salt.
        
        Args:
            password (str): Plain text password
            salt (Optional[str]): Salt for hashing (generated if not provided)
            
        Returns:
            Tuple[str, str]: (hashed_password, salt)
        """
        if not salt:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA-256 for secure password hashing
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            password (str): Plain text password to verify
            stored_hash (str): Stored password hash
            salt (str): Salt used for hashing
            
        Returns:
            bool: True if password matches
        """
        computed_hash, _ = self.hash_password(password, salt)
        return secrets.compare_digest(computed_hash, stored_hash)
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength according to healthcare security standards.
        
        Args:
            password (str): Password to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        
        # Check for required character types
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            return False, "Password must contain uppercase, lowercase, digit, and special character"
        
        # Check for common weak patterns
        weak_patterns = ['password', '123456', 'qwerty', 'admin', 'user']
        if any(pattern in password.lower() for pattern in weak_patterns):
            return False, "Password contains common weak patterns"
        
        return True, "Password is strong"
    
    def create_session(self, user_id: int, ip_address: str, user_agent: str) -> str:
        """
        Create secure user session.
        
        Args:
            user_id (int): User ID
            ip_address (str): User's IP address
            user_agent (str): User's browser user agent
            
        Returns:
            str: Session ID
        """
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(seconds=self.session_timeout)
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO user_sessions (id, user_id, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_id, expires_at, ip_address, user_agent))
        conn.commit()
        conn.close()
        
        # Log session creation
        log_audit_event(user_id, 'SESSION_CREATE', 'session', None, 
                       f'{{"session_id": "{session_id}"}}', ip_address, user_agent)
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Validate and refresh user session.
        
        Args:
            session_id (str): Session ID to validate
            
        Returns:
            Optional[Dict[str, Any]]: Session data if valid, None otherwise
        """
        conn = get_db_connection()
        
        session_data = conn.execute('''
            SELECT s.*, u.username, u.role, u.email
            FROM user_sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.id = ? AND s.is_active = 1 AND s.expires_at > CURRENT_TIMESTAMP
        ''', (session_id,)).fetchone()
        
        if session_data:
            # Extend session expiration
            new_expires = datetime.utcnow() + timedelta(seconds=self.session_timeout)
            conn.execute('''
                UPDATE user_sessions 
                SET expires_at = ? 
                WHERE id = ?
            ''', (new_expires, session_id))
            conn.commit()
        
        conn.close()
        return dict(session_data) if session_data else None
    
    def invalidate_session(self, session_id: str, user_id: Optional[int] = None):
        """
        Invalidate a user session.
        
        Args:
            session_id (str): Session ID to invalidate
            user_id (Optional[int]): User ID for audit logging
        """
        conn = get_db_connection()
        conn.execute('''
            UPDATE user_sessions 
            SET is_active = 0 
            WHERE id = ?
        ''', (session_id,))
        conn.commit()
        conn.close()
        
        # Log session invalidation
        if user_id:
            log_audit_event(user_id, 'SESSION_INVALIDATE', 'session', None,
                           f'{{"session_id": "{session_id}"}}')
    
    def check_login_attempts(self, username: str, ip_address: str) -> Tuple[bool, int]:
        """
        Check if user/IP is locked out due to failed login attempts.
        
        Args:
            username (str): Username attempting login
            ip_address (str): IP address of login attempt
            
        Returns:
            Tuple[bool, int]: (is_locked_out, remaining_attempts)
        """
        conn = get_db_connection()
        
        # Check recent failed attempts
        lockout_time = datetime.utcnow() - timedelta(seconds=self.lockout_duration)
        
        attempts = conn.execute('''
            SELECT COUNT(*) as count FROM audit_log
            WHERE (details LIKE ? OR ip_address = ?)
            AND action = 'LOGIN_FAILED'
            AND timestamp > ?
        ''', (f'%{username}%', ip_address, lockout_time)).fetchone()
        
        conn.close()
        
        failed_attempts = attempts['count']
        remaining_attempts = max(0, self.max_login_attempts - failed_attempts)
        is_locked_out = failed_attempts >= self.max_login_attempts
        
        return is_locked_out, remaining_attempts
    
    def log_login_attempt(self, username: str, success: bool, ip_address: str, 
                         user_agent: str, user_id: Optional[int] = None):
        """
        Log login attempt for security monitoring.
        
        Args:
            username (str): Username used in login attempt
            success (bool): Whether login was successful
            ip_address (str): IP address of attempt
            user_agent (str): Browser user agent
            user_id (Optional[int]): User ID if login successful
        """
        action = 'LOGIN_SUCCESS' if success else 'LOGIN_FAILED'
        details = f'{{"username": "{username}", "success": {str(success).lower()}}}'
        
        log_audit_event(user_id, action, 'authentication', user_id, 
                       details, ip_address, user_agent)
    
    def get_user_permissions(self, role: str) -> Dict[str, bool]:
        """
        Get permissions for a user role.
        
        Args:
            role (str): User role (patient, social_worker, admin)
            
        Returns:
            Dict[str, bool]: Permission mappings
        """
        permissions = {
            'patient': {
                'view_own_images': True,
                'upload_images': True,
                'edit_own_narratives': True,
                'delete_own_images': True,
                'view_others_images': False,
                'admin_access': False,
                'moderate_content': False,
                'manage_users': False
            },
            'social_worker': {
                'view_own_images': True,
                'upload_images': True,
                'edit_own_narratives': True,
                'delete_own_images': True,
                'view_others_images': True,
                'admin_access': False,
                'moderate_content': True,
                'manage_users': False,
                'add_clinical_notes': True
            },
            'admin': {
                'view_own_images': True,
                'upload_images': True,
                'edit_own_narratives': True,
                'delete_own_images': True,
                'view_others_images': True,
                'admin_access': True,
                'moderate_content': True,
                'manage_users': True,
                'system_diagnostics': True,
                'audit_access': True
            }
        }
        
        return permissions.get(role, permissions['patient'])
    
    def has_permission(self, user_role: str, permission: str) -> bool:
        """
        Check if user role has specific permission.
        
        Args:
            user_role (str): User's role
            permission (str): Permission to check
            
        Returns:
            bool: True if user has permission
        """
        permissions = self.get_user_permissions(user_role)
        return permissions.get(permission, False)


def require_permission(permission: str):
    """
    Decorator to require specific permission for route access.
    
    Args:
        permission (str): Required permission
        
    Returns:
        function: Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            
            auth_manager = AuthManager()
            user_role = session.get('role', 'patient')
            
            if not auth_manager.has_permission(user_role, permission):
                if request.is_json:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                flash('You do not have permission to access this resource.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_role(required_role: str):
    """
    Decorator to require specific role for route access.
    
    Args:
        required_role (str): Required user role
        
    Returns:
        function: Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            
            user_role = session.get('role', 'patient')
            
            # Define role hierarchy
            role_hierarchy = {
                'patient': 0,
                'social_worker': 1,
                'admin': 2
            }
            
            user_level = role_hierarchy.get(user_role, 0)
            required_level = role_hierarchy.get(required_role, 2)
            
            if user_level < required_level:
                if request.is_json:
                    return jsonify({'error': 'Insufficient role level'}), 403
                flash(f'{required_role.title()} access required.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class SecurityManager:
    """
    Additional security utilities for BHV application.
    
    Provides security monitoring, threat detection, and compliance features.
    """
    
    def __init__(self):
        """Initialize security manager."""
        self.suspicious_patterns = [
            'script', 'javascript:', 'onload', 'onerror', 'onclick',
            'eval(', 'document.', 'window.', 'alert(', 'confirm('
        ]
    
    def sanitize_input(self, input_text: str) -> str:
        """
        Sanitize user input to prevent XSS and injection attacks.
        
        Args:
            input_text (str): User input to sanitize
            
        Returns:
            str: Sanitized input
        """
        if not input_text:
            return ""
        
        # Remove potentially dangerous patterns
        sanitized = input_text
        for pattern in self.suspicious_patterns:
            sanitized = sanitized.replace(pattern, '')
        
        # Basic HTML entity encoding
        sanitized = (sanitized
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#x27;'))
        
        return sanitized.strip()
    
    def detect_suspicious_activity(self, user_id: int, action: str, 
                                 ip_address: str) -> bool:
        """
        Detect potentially suspicious user activity.
        
        Args:
            user_id (int): User ID
            action (str): Action being performed
            ip_address (str): User's IP address
            
        Returns:
            bool: True if activity appears suspicious
        """
        conn = get_db_connection()
        
        # Check for rapid successive actions (potential automation)
        recent_actions = conn.execute('''
            SELECT COUNT(*) as count FROM audit_log
            WHERE user_id = ? AND timestamp > datetime('now', '-1 minute')
        ''', (user_id,)).fetchone()
        
        if recent_actions['count'] > 10:  # More than 10 actions per minute
            conn.close()
            return True
        
        # Check for multiple IP addresses (potential account sharing)
        recent_ips = conn.execute('''
            SELECT COUNT(DISTINCT ip_address) as count FROM audit_log
            WHERE user_id = ? AND timestamp > datetime('now', '-1 hour')
        ''', (user_id,)).fetchone()
        
        conn.close()
        
        if recent_ips['count'] > 3:  # More than 3 different IPs in an hour
            return True
        
        return False
    
    def get_security_headers(self) -> Dict[str, str]:
        """
        Get security headers for HTTP responses.
        
        Returns:
            Dict[str, str]: Security headers
        """
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }