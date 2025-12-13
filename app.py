"""Main BHV Flask application."""
from flask import Flask, render_template, request, redirect, url_for, flash, session
from bhv.database import db, init_db
from bhv.models import User, UserRole
from bhv.security import PasswordManager, Validator
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bhv.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)


@app.route('/')
def index():
    """Home page."""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', user=user)
    return render_template('index.html', user=None)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate email
        if not Validator.validate_email(email):
            flash('Invalid email format', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        # Validate password strength
        valid, error = PasswordManager.validate_password_strength(password)
        if not valid:
            flash(error, 'error')
            return render_template('register.html')
        
        # Create user
        try:
            hashed_password = PasswordManager.hash_password(password)
            user = User(
                email=email,
                password_hash=hashed_password,
                role=UserRole.PATIENT
            )
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f"Registration failed: {e}")
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Validate inputs
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not PasswordManager.verify_password(password, user.password_hash):
            flash('Invalid email or password', 'error')
            return render_template('login.html')
        
        # Create session
        session['user_id'] = user.id
        session['email'] = user.email
        session['role'] = user.role.value
        
        flash(f'Welcome back, {user.email}!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    """User dashboard (requires login)."""
    if 'user_id' not in session:
        flash('Please login to access dashboard', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)


@app.route('/logout')
def logout():
    """User logout."""
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))


@app.cli.command()
def init_database():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print("Database initialized!")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)