"""
BHV - Biomedical Histology Viewer
Main Flask application with user authentication and admin features
"""

from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
import os
import re
import secrets

# Initialize Flask app
app = Flask(__name__)

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent

# Production vs Development config
if os.environ.get('FLASK_ENV') == 'production':
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key-change-this')
    DATABASE_PATH = os.environ.get('DATABASE_URL', '/opt/render/project/src/bhv.db')
else:
    SECRET_KEY = 'dev-secret-key-change-in-production'
    DATABASE_PATH = str(BASE_DIR / 'bhv.db')

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
app.config['UPLOAD_FOLDER'] = str(BASE_DIR / 'static' / 'uploads')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ==================== MODELS ====================

class User(UserMixin, db.Model):
    """User model with authentication and admin support"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    images = db.relationship('Image', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Image(db.Model):
    """Image model for uploaded files"""
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Image {self.title}>'


# ==================== FORMS ====================

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ImageUploadForm(FlaskForm):
    """Image upload form"""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=3, max=200, message='Title must be between 3 and 200 characters')
    ])
    description = TextAreaField('Description', validators=[
        Length(max=1000, message='Description cannot exceed 1000 characters')
    ])
    file = FileField('Image File', validators=[DataRequired()])
    submit = SubmitField('Upload')


# ==================== HELPER FUNCTIONS ====================

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def sanitize_filename(filename):
    """Sanitize filename to prevent security issues"""
    filename = secure_filename(filename)
    name, ext = os.path.splitext(filename)
    name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    name = re.sub(r'[-\s]+', '-', name)
    return name + ext


def get_unique_filename(filename):
    """Generate unique filename to avoid collisions"""
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_str = secrets.token_hex(4)
    return f"{name}_{timestamp}_{random_str}{ext}"


# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account created successfully! Welcome, {user.username}!', 'success')
        login_user(user)
        return redirect(url_for('profile'))
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('profile'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user_images = Image.query.filter_by(user_id=current_user.id).order_by(Image.uploaded_at.desc()).all()
    return render_template('profile.html', images=user_images)


# ==================== IMAGE ROUTES ====================

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Image upload page"""
    form = ImageUploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        
        if not file or file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash(f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}', 'danger')
            return redirect(request.url)
        
        # Sanitize and generate unique filename
        original_filename = sanitize_filename(file.filename)
        unique_filename = get_unique_filename(original_filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(filepath)
        file_size = os.path.getsize(filepath)
        
        # Create database entry
        image = Image(
            filename=unique_filename,
            title=form.title.data,
            description=form.description.data,
            file_size=file_size,
            user_id=current_user.id
        )
        
        db.session.add(image)
        db.session.commit()
        
        flash('Image uploaded successfully!', 'success')
        return redirect(url_for('gallery'))
    
    return render_template('upload.html', form=form)


@app.route('/gallery')
@login_required
def gallery():
    """
    Gallery page with search and filter functionality
    Users can search by title/description and sort images
    """
    # Get search query from URL parameters
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'newest')  # newest, oldest, name, size
    
    # Base query - only current user's images
    query = Image.query.filter_by(user_id=current_user.id)
    
    # Apply search filter if provided
    if search_query:
        search_filter = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Image.title.ilike(search_filter),
                Image.description.ilike(search_filter)
            )
        )
    
    # Apply sorting
    if sort_by == 'newest':
        query = query.order_by(Image.uploaded_at.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Image.uploaded_at.asc())
    elif sort_by == 'name':
        query = query.order_by(Image.title.asc())
    elif sort_by == 'size':
        query = query.order_by(Image.file_size.desc())
    
    # Limit to 50 images for performance
    images = query.limit(50).all()
    
    # Get total count for display
    total_count = Image.query.filter_by(user_id=current_user.id).count()
    
    return render_template('gallery.html', 
                         images=images, 
                         search_query=search_query,
                         sort_by=sort_by,
                         total_count=total_count)


@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics"""
    total_users = User.query.count()
    total_images = Image.query.count()
    
    # Calculate total storage
    total_storage = db.session.query(db.func.sum(Image.file_size)).scalar() or 0
    total_storage_mb = round(total_storage / (1024 * 1024), 2)
    
    # Top uploaders
    top_uploaders = db.session.query(
        User, db.func.count(Image.id).label('image_count')
    ).join(Image).group_by(User.id).order_by(db.desc('image_count')).limit(5).all()
    
    # Recent images
    recent_images = Image.query.order_by(Image.uploaded_at.desc()).limit(6).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_images=total_images,
                         total_storage_mb=total_storage_mb,
                         top_uploaders=top_uploaders,
                         recent_images=recent_images)


@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin user management"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = User.query
    if search:
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html', users=users, search=search)


@app.route('/admin/users/<int:user_id>')
@admin_required
def admin_user_detail(user_id):
    """Admin user detail page"""
    user = User.query.get_or_404(user_id)
    images = Image.query.filter_by(user_id=user_id).order_by(Image.uploaded_at.desc()).all()
    
    # Calculate user's storage
    total_storage = sum(img.file_size for img in images)
    total_storage_mb = round(total_storage / (1024 * 1024), 2)
    
    return render_template('admin/user_detail.html', user=user, images=images, total_storage_mb=total_storage_mb)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Admin delete user"""
    if user_id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(user_id)
    
    # Delete user's image files
    for image in user.images:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    # Delete user (cascade will delete images)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} and all their images have been deleted.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def admin_toggle_admin(user_id):
    """Toggle admin status for user"""
    if user_id == current_user.id:
        flash('You cannot change your own admin status!', 'danger')
        return redirect(url_for('admin_user_detail', user_id=user_id))
    
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'Admin' if user.is_admin else 'Regular User'
    flash(f'{user.username} is now a {status}.', 'success')
    return redirect(url_for('admin_user_detail', user_id=user_id))


@app.route('/admin/images')
@admin_required
def admin_images():
    """Admin image management"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Image.query
    if search:
            db.or_(
                Image.title.ilike(f'%{search}%'),
                Image.description.ilike(f'%{search}%')
            )
    
    images = query.order_by(Image.uploaded_at.desc()).paginate(page=page, per_page=24, error_out=False)
    
    return render_template('admin/images.html', images=images, search=search)


@app.route('/admin/images/<int:image_id>/delete', methods=['POST'])
@admin_required
def admin_delete_image(image_id):
    """Admin delete image"""
    image = Image.query.get_or_404(image_id)
    
    # Delete file from disk
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # Delete from database
    db.session.delete(image)
    db.session.commit()
    
    flash(f'Image "{image.title}" has been deleted.', 'success')
    
    # Redirect back to referring page
    return redirect(request.referrer or url_for('admin_images'))


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors with custom page"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with custom page"""
    db.session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 Forbidden errors"""
    return render_template('errors/403.html'), 403


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors"""
    flash('File is too large! Maximum size is 5MB.', 'danger')
    return redirect(request.referrer or url_for('upload'))


# ==================== APPLICATION FACTORY ====================

def create_app():
    """Application factory for deployment"""
    with app.app_context():
        db.create_all()
    return app


# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin accounts if they don't exist (for local development)
        admins = [
            ('yadavchiragg', 'yadav@bhv.com', 'Demo2024!'),
            ('pradeeban', 'pradeeban@bhv.com', 'BHV2024!'),
            ('mdxabu', 'mdxabu@bhv.com', 'BHV2024!')
        ]
        
        for username, email, password in admins:
            if not User.query.filter_by(username=username).first():
                user = User(username=username, email=email, is_admin=True)
                user.set_password(password)
                db.session.add(user)
                print(f'✅ Created admin: {username}')
        
        db.session.commit()
    
    app.run(host='0.0.0.0', port=5000, debug=True)