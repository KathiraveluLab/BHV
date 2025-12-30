#!/usr/bin/env python3
"""
BHV: Behavioral Health Vault
Main application entry point for the healthcare image and narrative storage system.

This module provides the core Flask application with authentication, file handling,
and database management for storing patient-provided images and narratives.
"""

import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import logging
from functools import wraps

from config.settings import Config
from models.database import init_db, get_db_connection
from utils.file_handler import FileHandler
from utils.auth import AuthManager
from utils.diagnostics import DiagnosticsManager


def create_app():
    """
    Application factory pattern for creating Flask app instance.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = Config()
    app.config.update(config.get_flask_config())
    
    # Initialize logging
    setup_logging(app)
    
    # Initialize database
    init_db()
    
    # Initialize utilities
    file_handler = FileHandler(app.config['UPLOAD_FOLDER'])
    auth_manager = AuthManager()
    diagnostics = DiagnosticsManager()
    
    # Store utilities in app context
    app.file_handler = file_handler
    app.auth_manager = auth_manager
    app.diagnostics = diagnostics
    
    # Register routes
    register_routes(app)
    
    app.logger.info("BHV application initialized successfully")
    return app


def setup_logging(app):
    """
    Configure application logging with file and console handlers.
    
    Args:
        app (Flask): Flask application instance
    """
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('logs/bhv.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def login_required(f):
    """
    Decorator to require user authentication for protected routes.
    
    Args:
        f (function): Route function to protect
        
    Returns:
        function: Wrapped function with authentication check
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin privileges for protected routes.
    
    Args:
        f (function): Route function to protect
        
    Returns:
        function: Wrapped function with admin check
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT role FROM users WHERE id = ?', (session['user_id'],)
        ).fetchone()
        conn.close()
        
        if not user or user['role'] != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def register_routes(app):
    """
    Register all application routes with the Flask app.
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.route('/')
    def index():
        """Home page route."""
        return render_template('index.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration route."""
        if request.method == 'POST':
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            role = request.form.get('role', 'patient')
            
            # Validate input
            if not all([email, username, password]):
                flash('All fields are required.', 'error')
                return render_template('register.html')
            
            # Check if user exists
            conn = get_db_connection()
            existing_user = conn.execute(
                'SELECT id FROM users WHERE email = ? OR username = ?',
                (email, username)
            ).fetchone()
            
            if existing_user:
                flash('User already exists.', 'error')
                conn.close()
                return render_template('register.html')
            
            # Create user
            password_hash = generate_password_hash(password)
            conn.execute(
                'INSERT INTO users (email, username, password_hash, role) VALUES (?, ?, ?, ?)',
                (email, username, password_hash, role)
            )
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please log in.', 'success')
            app.logger.info(f"New user registered: {username} ({email})")
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login route."""
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            conn = get_db_connection()
            user = conn.execute(
                'SELECT * FROM users WHERE username = ?', (username,)
            ).fetchone()
            conn.close()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                
                app.logger.info(f"User logged in: {username}")
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'error')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """User logout route."""
        username = session.get('username', 'Unknown')
        session.clear()
        app.logger.info(f"User logged out: {username}")
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard route."""
        conn = get_db_connection()
        
        if session['role'] == 'admin':
            # Admin sees all images
            images = conn.execute('''
                SELECT i.*, u.username 
                FROM images i 
                JOIN users u ON i.user_id = u.id 
                ORDER BY i.created_at DESC
            ''').fetchall()
        else:
            # Users see only their images
            images = conn.execute(
                'SELECT * FROM images WHERE user_id = ? ORDER BY created_at DESC',
                (session['user_id'],)
            ).fetchall()
        
        conn.close()
        return render_template('dashboard.html', images=images)
    
    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload():
        """Image upload route."""
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file selected.', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            narrative = request.form.get('narrative', '')
            
            if file.filename == '':
                flash('No file selected.', 'error')
                return redirect(request.url)
            
            if file and app.file_handler.allowed_file(file.filename):
                try:
                    # Save file
                    file_path = app.file_handler.save_file(file, session['user_id'])
                    
                    # Save to database
                    conn = get_db_connection()
                    conn.execute('''
                        INSERT INTO images (user_id, filename, file_path, narrative)
                        VALUES (?, ?, ?, ?)
                    ''', (session['user_id'], secure_filename(file.filename), file_path, narrative))
                    conn.commit()
                    conn.close()
                    
                    app.logger.info(f"File uploaded by {session['username']}: {file.filename}")
                    flash('File uploaded successfully!', 'success')
                    return redirect(url_for('dashboard'))
                
                except Exception as e:
                    app.logger.error(f"Upload error: {str(e)}")
                    flash('Upload failed. Please try again.', 'error')
            else:
                flash('Invalid file type. Please upload an image.', 'error')
        
        return render_template('upload.html')
    
    @app.route('/admin')
    @admin_required
    def admin_panel():
        """Admin panel route."""
        conn = get_db_connection()
        
        # Get statistics
        stats = {
            'total_users': conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count'],
            'total_images': conn.execute('SELECT COUNT(*) as count FROM images').fetchone()['count'],
            'recent_uploads': conn.execute('''
                SELECT i.*, u.username 
                FROM images i 
                JOIN users u ON i.user_id = u.id 
                ORDER BY i.created_at DESC 
                LIMIT 10
            ''').fetchall()
        }
        
        conn.close()
        return render_template('admin.html', stats=stats)
    
    @app.route('/diagnostics')
    @admin_required
    def diagnostics():
        """System diagnostics route."""
        diagnostic_results = app.diagnostics.run_full_diagnostics()
        return render_template('diagnostics.html', results=diagnostic_results)
    
    @app.route('/api/health')
    def health_check():
        """Health check API endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })


if __name__ == '__main__':
    """
    Main entry point for the BHV application.
    Starts the Flask development server with configuration from environment.
    """
    app = create_app()
    
    # Get server configuration
    config = Config()
    server_config = config.get_server_config()
    
    print("=" * 50)
    print("🏥 BHV: Behavioral Health Vault")
    print("=" * 50)
    print(f"🌐 Server: http://{server_config['host']}:{server_config['port']}")
    print(f"🔧 Debug Mode: {server_config['debug']}")
    print(f"📁 Upload Directory: {app.config['UPLOAD_FOLDER']}")
    print("=" * 50)
    
    try:
        app.run(
            host=server_config['host'],
            port=server_config['port'],
            debug=server_config['debug']
        )
    except KeyboardInterrupt:
        print("\n👋 BHV application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start BHV application: {e}")
        sys.exit(1)