"""
BHV - Biomedical Histology Vault
A secure platform for storing and sharing biomedical histology images
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import secrets
import csv
import json
from io import StringIO, BytesIO

# ==================== APP CONFIGURATION ====================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration - Fix for Render PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bhv.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# ==================== DATABASE MODELS ====================

class User(UserMixin, db.Model):
    """User model for authentication and profile"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with images
    images = db.relationship('Image', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Image(db.Model):
    """Image model for storing user uploads"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_size = db.Column(db.Integer)  # Size in bytes
    
    def __repr__(self):
        return f'<Image {self.title}>'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_unique_filename(filename):
    """Generate unique filename to prevent collisions"""
    name, ext = os.path.splitext(filename)
    unique_name = f"{secure_filename(name)}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}{ext}"
    return unique_name


def format_file_size(size_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('gallery'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'danger')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('gallery'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page if next_page else url_for('gallery'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Image upload page"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validation
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        if not title:
            flash('Title is required.', 'danger')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP, WEBP', 'danger')
            return redirect(request.url)
        
        # Save file
        filename = get_unique_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Save to database
        image = Image(
            filename=filename,
            title=title,
            description=description,
            user_id=current_user.id,
            file_size=file_size
        )
        db.session.add(image)
        db.session.commit()
        
        flash(f'Image "{title}" uploaded successfully!', 'success')
        return redirect(url_for('gallery'))
    
    return render_template('upload.html')


@app.route('/gallery')
@login_required
def gallery():
    """Image gallery - users see only their images, admins see all"""
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'date_desc')
    
    # Base query
    if current_user.is_admin:
        query = Image.query
    else:
        query = Image.query.filter_by(user_id=current_user.id)
    
    # Search filter
    if search_query:
        query = query.filter(
            db.or_(
                Image.title.ilike(f'%{search_query}%'),
                Image.description.ilike(f'%{search_query}%')
            )
        )
    
    # Sorting
    if sort_by == 'date_asc':
        query = query.order_by(Image.upload_date.asc())
    elif sort_by == 'date_desc':
        query = query.order_by(Image.upload_date.desc())
    elif sort_by == 'title_asc':
        query = query.order_by(Image.title.asc())
    elif sort_by == 'title_desc':
        query = query.order_by(Image.title.desc())
    elif sort_by == 'size_asc':
        query = query.order_by(Image.file_size.asc())
    elif sort_by == 'size_desc':
        query = query.order_by(Image.file_size.desc())
    
    images = query.all()
    
    return render_template('gallery.html', images=images, format_size=format_file_size)


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user_images = Image.query.filter_by(user_id=current_user.id).all()
    total_storage = sum(img.file_size for img in user_images)
    
    return render_template('profile.html', 
                         user=current_user, 
                         image_count=len(user_images),
                         total_storage=format_file_size(total_storage),
                         recent_images=user_images[:5])


@app.route('/delete/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    """Delete an image"""
    image = Image.query.get_or_404(image_id)
    
    # Check permissions
    if not current_user.is_admin and image.user_id != current_user.id:
        flash('You do not have permission to delete this image.', 'danger')
        return redirect(url_for('gallery'))
    
    # Delete file from filesystem
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # Delete from database
    db.session.delete(image)
    db.session.commit()
    
    flash(f'Image "{image.title}" deleted successfully.', 'success')
    return redirect(url_for('gallery'))


# ==================== EXPORT ROUTES ====================

@app.route('/export/my-data/csv')
@login_required
def export_my_data_csv():
    """Export user's own data as CSV"""
    images = Image.query.filter_by(user_id=current_user.id).order_by(Image.upload_date.desc()).all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Image Title', 'Description', 'Filename', 'Size (bytes)', 'Upload Date'])
    
    for image in images:
        writer.writerow([
            image.title,
            image.description or '',
            image.filename,
            image.file_size or 0,
            image.upload_date.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Prepare file for download
    output.seek(0)
    filename = f"bhv_my_data_{current_user.username}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    
    return send_file(
        BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@app.route('/export/my-data/json')
@login_required
def export_my_data_json():
    """Export user's own data as JSON"""
    images = Image.query.filter_by(user_id=current_user.id).order_by(Image.upload_date.desc()).all()
    
    data = {
        'user': {
            'username': current_user.username,
            'email': current_user.email,
            'member_since': current_user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        },
        'images': [
            {
                'title': img.title,
                'description': img.description or '',
                'filename': img.filename,
                'size_bytes': img.file_size or 0,
                'upload_date': img.upload_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            for img in images
        ],
        'export_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    filename = f"bhv_my_data_{current_user.username}_{datetime.utcnow().strftime('%Y%m%d')}.json"
    
    return send_file(
        BytesIO(json.dumps(data, indent=2).encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )


# ==================== ADMIN ROUTES ====================

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    total_users = User.query.count()
    total_images = Image.query.count()
    total_storage = db.session.query(db.func.sum(Image.file_size)).scalar() or 0
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_images = Image.query.order_by(Image.upload_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_images=total_images,
                         total_storage=format_file_size(total_storage),
                         recent_users=recent_users,
                         recent_images=recent_images)


@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin user management"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/images')
@login_required
@admin_required
def admin_images():
    """Admin image management"""
    images = Image.query.order_by(Image.upload_date.desc()).all()
    return render_template('admin/images.html', images=images, format_size=format_file_size)


@app.route('/admin/export/users/csv')
@login_required
@admin_required
def admin_export_users_csv():
    """Export all users as CSV"""
    users = User.query.order_by(User.created_at.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Username', 'Email', 'Is Admin', 'Image Count', 'Total Storage', 'Join Date'])
    
    for user in users:
        image_count = Image.query.filter_by(user_id=user.id).count()
        total_storage = db.session.query(db.func.sum(Image.file_size)).filter(Image.user_id == user.id).scalar() or 0
        
        writer.writerow([
            user.username,
            user.email,
            'Yes' if user.is_admin else 'No',
            image_count,
            total_storage,
            user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    filename = f"bhv_all_users_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    
    return send_file(
        BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@app.route('/admin/export/images/csv')
@login_required
@admin_required
def admin_export_images_csv():
    """Export all images as CSV"""
    images = Image.query.order_by(Image.upload_date.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Title', 'Owner', 'Filename', 'Size (bytes)', 'Upload Date'])
    
    for image in images:
        writer.writerow([
            image.title,
            image.owner.username,
            image.filename,
            image.file_size or 0,
            image.upload_date.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    filename = f"bhv_all_images_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    
    return send_file(
        BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


# ==================== ERROR HANDLERS ====================

@app.errorhandler(403)
def forbidden(e):
    """403 Forbidden error handler"""
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def not_found(e):
    """404 Not Found error handler"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """500 Internal Server Error handler"""
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ==================== RUN APP ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)