"""Authentication and authorization decorators."""
from functools import wraps
from flask import redirect, url_for, flash, jsonify, request
from flask_login import current_user


def login_required_custom(f):
    """Custom login required decorator with better error handling."""
    from flask_login import login_required
    
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Additional check for verified users
        if not current_user.is_verified:
            flash('Please verify your email before accessing this page.', 'warning')
            return redirect(url_for('auth.register'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role.
    Works for both regular routes and API routes.
    """
    from flask_login import login_required
    
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_verified:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Email verification required'}), 403
            flash('Please verify your email before accessing this page.', 'warning')
            return redirect(url_for('auth.register'))
        
        # Check if user is admin (dynamically checks ADMIN_EMAILS at runtime)
        # Always reads ADMIN_EMAILS fresh from .env file
        from app.config import is_admin_email
        
        # Check if email is in ADMIN_EMAILS (always fresh from .env)
        is_admin = is_admin_email(current_user.email)
        
        # Also check stored role as fallback
        if not is_admin:
            is_admin = current_user.get_stored_role() == 'admin'
        
        if not is_admin:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Admin access required'}), 403
            flash('Admin access required.', 'error')
            return redirect(url_for('uploads.gallery'))
        
        return f(*args, **kwargs)
    return decorated_function


def verified_user_required(f):
    """
    Decorator to require verified email.
    Users must verify their email before accessing protected routes.
    """
    from flask_login import login_required
    
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_verified:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Email verification required'}), 403
            flash('Please verify your email before accessing this page.', 'warning')
            return redirect(url_for('auth.register'))
        return f(*args, **kwargs)
    return decorated_function


def user_only(f):
    """
    Decorator to allow only regular users (not admins).
    Admins are blocked from accessing user-only routes like uploads.
    """
    from flask_login import login_required
    from app.config import is_admin_email
    
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_verified:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Email verification required'}), 403
            flash('Please verify your email before accessing this page.', 'warning')
            return redirect(url_for('auth.register'))
        
        # Check if user is admin (dynamically checks ADMIN_EMAILS at runtime)
        is_admin = is_admin_email(current_user.email)
        
        # Also check stored role as fallback
        if not is_admin:
            is_admin = current_user.get_stored_role() == 'admin'
        
        if is_admin:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Admin access not allowed. This feature is for regular users only.'}), 403
            flash('Admin users cannot access this feature. Please use the admin dashboard.', 'error')
            return redirect(url_for('admin.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

