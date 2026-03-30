import os
from datetime import datetime, timedelta
from io import BytesIO, StringIO
import csv
import json
import time
from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

# ============================================
# FLASK APP CONFIGURATION
# ============================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bhv.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
# Fix for Render PostgreSQL URL
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ============================================
# DATABASE MODELS
# ============================================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('Image', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(200), nullable=False)
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ============================================
# HELPER FUNCTIONS
# ============================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(filename):
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{secure_filename(name)}_{timestamp}{ext}"

# ============================================
# EXPORT HELPER FUNCTIONS
# ============================================

def generate_user_data_csv(user):
    """Generate CSV export of user's images"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Image Title', 'Description', 'Filename', 'File Size (KB)', 'Upload Date'])
    
    # Write data
    for image in user.images:
        writer.writerow([
            image.title,
            image.description or 'No description',
            image.filename,
            round(image.file_size / 1024, 2),
            image.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Convert to bytes
    output.seek(0)
    bytes_output = BytesIO()
    bytes_output.write(output.getvalue().encode('utf-8-sig'))  # UTF-8 with BOM for Excel
    bytes_output.seek(0)
    
    return bytes_output

def generate_user_data_json(user):
    """Generate JSON export of user's complete data"""
    data = {
        'user': {
            'username': user.username,
            'email': user.email,
            'member_since': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_admin': user.is_admin,
            'total_images': len(user.images),
            'total_storage_mb': round(sum(img.file_size for img in user.images) / (1024 * 1024), 2)
        },
        'images': [
            {
                'id': img.id,
                'title': img.title,
                'description': img.description or 'No description',
                'filename': img.filename,
                'file_size_kb': round(img.file_size / 1024, 2),
                'uploaded_at': img.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for img in user.images
        ],
        'export_metadata': {
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'export_format': 'JSON',
            'version': '1.0'
        }
    }
    
    output = BytesIO()
    output.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))
    output.seek(0)
    
    return output

def generate_admin_users_csv():
    """Generate CSV export of all users (admin only)"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Username', 'Email', 'Is Admin', 'Total Images', 'Storage (MB)', 'Member Since'])
    
    # Write data
    users = User.query.all()
    for user in users:
        total_storage = sum(img.file_size for img in user.images) / (1024 * 1024)
        writer.writerow([
            user.username,
            user.email,
            'Yes' if user.is_admin else 'No',
            len(user.images),
            round(total_storage, 2),
            user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Convert to bytes
    output.seek(0)
    bytes_output = BytesIO()
    bytes_output.write(output.getvalue().encode('utf-8-sig'))
    bytes_output.seek(0)
    
    return bytes_output

def generate_admin_images_csv():
    """Generate CSV export of all images (admin only)"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Image ID', 'Title', 'Owner', 'Owner Email', 'Filename', 'File Size (KB)', 'Upload Date'])
    
    # Write data
    images = Image.query.order_by(Image.uploaded_at.desc()).all()
    for image in images:
        writer.writerow([
            image.id,
            image.title,
            image.owner.username,
            image.owner.email,
            image.filename,
            round(image.file_size / 1024, 2),
            image.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Convert to bytes
    output.seek(0)
    bytes_output = BytesIO()
    bytes_output.write(output.getvalue().encode('utf-8-sig'))
    bytes_output.seek(0)
    
    return bytes_output

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('profile'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/ping')
@login_required
def ping():
    """Keep session alive endpoint for session timeout feature"""
    return jsonify({'status': 'ok', 'timestamp': time.time()})

# ============================================
# USER ROUTES
# ============================================

@app.route('/profile')
@login_required
def profile():
    images = Image.query.filter_by(user_id=current_user.id).order_by(Image.uploaded_at.desc()).all()
    return render_template('profile.html', images=images)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(url_for('upload'))
        
        file = request.files['file']
        title = request.form.get('title')
        description = request.form.get('description')
        
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('upload'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.', 'danger')
            return redirect(url_for('upload'))
        
        if not title:
            flash('Please provide a title for your image.', 'danger')
            return redirect(url_for('upload'))
        
        filename = get_unique_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        file_size = os.path.getsize(filepath)
        
        image = Image(
            title=title,
            description=description,
            filename=filename,
            file_size=file_size,
            user_id=current_user.id
        )
        db.session.add(image)
        db.session.commit()
        
        flash('Image uploaded successfully!', 'success')
        return redirect(url_for('gallery'))
    
    return render_template('upload.html')

@app.route('/gallery')
@login_required
def gallery():
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'newest')
    
    query = Image.query.filter_by(user_id=current_user.id)
    total_count = query.count()
    
    if search_query:
        query = query.filter(
            db.or_(
                Image.title.ilike(f'%{search_query}%'),
                Image.description.ilike(f'%{search_query}%')
            )
        )
    
    if sort_by == 'oldest':
        query = query.order_by(Image.uploaded_at.asc())
    elif sort_by == 'name':
        query = query.order_by(Image.title.asc())
    elif sort_by == 'size':
        query = query.order_by(Image.file_size.desc())
    else:  # newest
        query = query.order_by(Image.uploaded_at.desc())
    
    images = query.all()
    
    return render_template('gallery.html', images=images, search_query=search_query, 
                         sort_by=sort_by, total_count=total_count)

@app.route('/uploads/<filename>')
def serve_upload(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ============================================
# EXPORT ROUTES
# ============================================

@app.route('/export/my-data/csv')
@login_required
def export_my_data_csv():
    """Export user's data as CSV"""
    try:
        output = generate_user_data_csv(current_user)
        filename = f'bhv_my_data_{current_user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'danger')
        return redirect(url_for('profile'))

@app.route('/export/my-data/json')
@login_required
def export_my_data_json():
    """Export user's data as JSON"""
    try:
        output = generate_user_data_json(current_user)
        filename = f'bhv_my_data_{current_user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        return send_file(
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'danger')
        return redirect(url_for('profile'))

@app.route('/admin/export/users')
@login_required
@admin_required
def admin_export_users():
    """Export all users as CSV (admin only)"""
    try:
        output = generate_admin_users_csv()
        filename = f'bhv_all_users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error exporting users: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/export/images')
@login_required
@admin_required
def admin_export_images():
    """Export all images as CSV (admin only)"""
    try:
        output = generate_admin_images_csv()
        filename = f'bhv_all_images_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error exporting images: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

# ============================================
# ADMIN ROUTES
# ============================================

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_images = Image.query.count()
    total_storage = db.session.query(db.func.sum(Image.file_size)).scalar() or 0
    total_storage_mb = round(total_storage / (1024 * 1024), 2)
    
    # Top uploaders
    from sqlalchemy import func
    top_uploaders = db.session.query(User, func.count(Image.id).label('count'))\
        .join(Image).group_by(User.id).order_by(func.count(Image.id).desc()).limit(5).all()
    
    # Recent images
    recent_images = Image.query.order_by(Image.uploaded_at.desc()).limit(6).all()
    
    # Uploads over last 7 days
    dates = [(datetime.now() - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
    uploads_counts = []
    for i in range(6, -1, -1):
        date = datetime.now() - timedelta(days=i)
        count = Image.query.filter(
            db.func.date(Image.uploaded_at) == date.date()
        ).count()
        uploads_counts.append(count)
    
    # Chart data
    top_uploaders_names = [u.username for u, _ in top_uploaders]
    top_uploaders_counts = [count for _, count in top_uploaders]
    
    # Storage distribution (top 5 users)
    storage_users = []
    storage_sizes = []
    for user, _ in top_uploaders[:5]:
        storage = sum(img.file_size for img in user.images) / (1024 * 1024)
        storage_users.append(user.username)
        storage_sizes.append(round(storage, 2))
    
    # User activity
    active_users = User.query.join(Image).distinct().count()
    inactive_users = total_users - active_users
    user_activity = [active_users, inactive_users]
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_images=total_images,
                         total_storage_mb=total_storage_mb,
                         top_uploaders=top_uploaders,
                         recent_images=recent_images,
                         uploads_dates=dates,
                         uploads_counts=uploads_counts,
                         top_uploaders_names=top_uploaders_names,
                         top_uploaders_counts=top_uploaders_counts,
                         storage_users=storage_users,
                         storage_sizes=storage_sizes,
                         user_activity=user_activity)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    user_stats = []
    for user in users:
        image_count = len(user.images)
        storage_mb = round(sum(img.file_size for img in user.images) / (1024 * 1024), 2)
        user_stats.append({
            'user': user,
            'image_count': image_count,
            'storage_mb': storage_mb
        })
    return render_template('admin/users.html', user_stats=user_stats)

@app.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def admin_toggle_admin(user_id):
    if user_id == current_user.id:
        flash('You cannot modify your own admin status.', 'danger')
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} for {user.username}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    if user_id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(user_id)
    
    # Delete user's image files
    for image in user.images:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} and all their images have been deleted.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/images')
@login_required
@admin_required
def admin_images():
    images = Image.query.order_by(Image.uploaded_at.desc()).all()
    return render_template('admin/images.html', images=images)

@app.route('/admin/images/<int:image_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_image(image_id):
    image = Image.query.get_or_404(image_id)
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    db.session.delete(image)
    db.session.commit()
    
    flash('Image deleted successfully.', 'success')
    return redirect(url_for('admin_images'))

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)