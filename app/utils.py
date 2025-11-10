"""Utility functions for the application."""
import secrets
import string
import smtplib
from flask import render_template, redirect, url_for, current_app
from flask_login import current_user
from email.mime.text import MIMEText


def index_route():
    """Home page route."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('uploads.gallery'))
    return redirect(url_for('auth.login'))


def generate_otp(length=6):
    """Generate a random OTP code."""
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def send_email_direct_smtp(to_email, subject, body):
    """
    Send email using direct SMTP connection as fallback.
    This bypasses Flask-Mail in case of authentication issues.
    """
    try:
        mail_server = current_app.config.get('MAIL_SERVER')
        mail_port = current_app.config.get('MAIL_PORT')
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')
        mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
        
        if not mail_username or not mail_password:
            return False, "Email credentials not configured"
        
        # Create SMTP connection
        server = smtplib.SMTP(mail_server, mail_port)
        
        if mail_use_tls:
            server.starttls()
        
        # Login
        server.login(mail_username, mail_password)
        
        # Create message
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = mail_username
        msg['To'] = to_email
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        return True, None
    except smtplib.SMTPAuthenticationError as e:
        return False, f"SMTP Authentication Error: {str(e)}"
    except Exception as e:
        return False, f"SMTP Error: {str(e)}"


def find_or_create_user_google(user_info):
    """Find or create user from Google OAuth info."""
    from app.models import User, get_db
    from bson import ObjectId
    
    google_id = user_info.get('sub')
    email = user_info.get('email')
    name = user_info.get('name', '')
    
    # Try to find by Google ID first
    user = User.find_by_google_id(google_id)
    if user:
        return user
    
    # Try to find by email
    user = User.find_by_email(email)
    if user:
        # Link Google account
        get_db().users.update_one(
            {'_id': ObjectId(user.id)},
            {'$set': {'google_id': google_id, 'is_verified': True}}
        )
        user.google_id = google_id
        user.is_verified = True
        return user
    
    # Create new user - role will be automatically determined from ADMIN_EMAILS
    # If email is in ADMIN_EMAILS list, role will be 'admin', otherwise 'user'
    user = User.create(
        email=email,
        role=None,  # Let User.create determine role from ADMIN_EMAILS
        google_id=google_id
    )
    return user
