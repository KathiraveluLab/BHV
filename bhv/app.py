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
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///bhv.db')
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
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)


class Image(db.Model):
    """Image model for uploaded files"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(300), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# ==================== FLASK-LOGIN CONFIGURATION ====================

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def sanitize_filename(filename):
    """Sanitize filename to prevent security issues"""
    filename = os.path.basename(filename)
    filename = secure_filename(filename)
    filename = filename.lower().replace(' ', '-')
    return filename


def get_unique_filename(filename):
    """Generate unique filename with timestamp and random string"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_str = secrets.token_hex(4)
    name, ext = os.path.splitext(sanitize_filename(filename))
    return f"{name}_{timestamp}_{random_str}{ext}"


def admin_required(f):
    """Decorator to require admin privileges"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('Admin privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== EXPORT HELPERS ====================

def generate_user_data_csv(user):
    """Generate CSV export of user's data"""
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Image Title', 'Description', 'Filename', 'File Size (KB)', 'Upload Date'])
    
    images = Image.query.filter_by(user_id=user.id).order_by(Image.uploaded_at.desc()).all()
    for image in images:
        writer.writerow([
            image.title,
            image.description or 'No description',
            image.filename,
            round(image.file_size / 1024, 2),
            image.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    return output.getvalue()


def generate_user_data_json(user):
    """Generate JSON export of user's data"""
    images = Image.query.filter_by(user_id=user.id).order_by(Image.uploaded_at.desc()).all()
    
    data = {
        'user': {
            'username': user.username,
            'email': user.email,
            'member_since': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'total_images': len(images),
            'total_storage_mb': round(sum(img.file_size for img in images) / (1024 * 1024), 2)
        },
        'images': [
            {
                'title': img.title,
                'description': img.description,
                'filename': img.filename,
                'file_size_kb': round(img.file_size / 1024, 2),
                'uploaded_at': img.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for img in images
        ],
        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return json.dumps(data, indent=2)


def generate_admin_users_csv():
    """Generate CSV of all users (admin only)"""
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Username', 'Email', 'Is Admin', 'Total Images', 'Storage (MB)', 'Member Since'])
    
    users = User.query.all()
    for user in users:
        image_count = Image.query.filter_by(user_id=user.id).count()
        total_storage = db.session.query(db.func.sum(Image.file_size)).filter_by(user_id=user.id).scalar() or 0
        
        writer.writerow([
            user.username,
            user.email,
            'Yes' if user.is_admin else 'No',
            image_count,
            round(total_storage / (1024 * 1024), 2),
            user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    return output.getvalue()


def generate_admin_images_csv():
    """Generate CSV of all images (admin only)"""
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Title', 'Owner', 'Filename', 'File Size (KB)', 'Upload Date'])
    
    images = Image.query.order_by(Image.uploaded_at.desc()).all()
    for image in images:
        writer.writerow([
            image.title,
            image.owner.username,
            image.filename,
            round(image.file_size / 1024, 2),
            image.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    return output.getvalue()


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
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
            flash('Username already taken.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
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
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page if next_page else url_for('profile'))
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


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    images = Image.query.filter_by(user_id=current_user.id).order_by(Image.uploaded_at.desc()).all()
    return render_template('profile.html', images=images)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Image upload page"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.', 'danger')
            return redirect(request.url)
        
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if not title:
            flash('Title is required.', 'danger')
            return redirect(request.url)
        
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
    """Gallery page with search and filter functionality"""
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'newest')
    
    query = Image.query.filter_by(user_id=current_user.id)
    
    if search_query:
        search_filter = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Image.title.ilike(search_filter),
                Image.description.ilike(search_filter)
            )
        )
    
    if sort_by == 'newest':
        query = query.order_by(Image.uploaded_at.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Image.uploaded_at.asc())
    elif sort_by == 'name':
        query = query.order_by(Image.title.asc())
    elif sort_by == 'size':
        query = query.order_by(Image.file_size.desc())
    
    images = query.limit(50).all()
    total_count = Image.query.filter_by(user_id=current_user.id).count()
    
    return render_template('gallery.html', 
                         images=images, 
                         search_query=search_query,
                         sort_by=sort_by,
                         total_count=total_count)


@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded images"""
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics and charts"""
    from datetime import timedelta
    
    total_users = User.query.count()
    total_images = Image.query.count()
    
    total_storage = db.session.query(db.func.sum(Image.file_size)).scalar() or 0
    total_storage_mb = round(total_storage / (1024 * 1024), 2)
    
    top_uploaders = db.session.query(
        User, db.func.count(Image.id).label('image_count')
    ).join(Image).group_by(User.id).order_by(db.desc('image_count')).limit(5).all()
    
    recent_images = Image.query.order_by(Image.uploaded_at.desc()).limit(6).all()
    
    # Chart data
    uploads_dates = []
    uploads_counts = []
    for i in range(6, -1, -1):
        date = datetime.now().date() - timedelta(days=i)
        count = Image.query.filter(
            db.func.date(Image.uploaded_at) == date
        ).count()
        uploads_dates.append(date.strftime('%b %d'))
        uploads_counts.append(count)
    
    top_uploaders_names = []
    top_uploaders_counts = []
    for user, count in top_uploaders[:5]:
        top_uploaders_names.append(user.username)
        top_uploaders_counts.append(count)
    
    storage_users = []
    storage_sizes = []
    top_storage_users = db.session.query(
        User,
        db.func.sum(Image.file_size).label('total_size')
    ).join(Image).group_by(User.id).order_by(db.desc('total_size')).limit(5).all()
    
    for user, total_size in top_storage_users:
        storage_users.append(user.username)
        storage_sizes.append(round(total_size / (1024 * 1024), 2))
    
    users_with_uploads = db.session.query(User.id).join(Image).distinct().count()
    users_without_uploads = total_users - users_with_uploads
    user_activity = [users_with_uploads, users_without_uploads]
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_images=total_images,
                         total_storage_mb=total_storage_mb,
                         top_uploaders=top_uploaders,
                         recent_images=recent_images,
                         uploads_dates=uploads_dates,
                         uploads_counts=uploads_counts,
                         top_uploaders_names=top_uploaders_names,
                         top_uploaders_counts=top_uploaders_counts,
                         storage_users=storage_users,
                         storage_sizes=storage_sizes,
                         user_activity=user_activity)


@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin user management page"""
    users = User.query.all()
    
    user_stats = []
    for user in users:
        image_count = Image.query.filter_by(user_id=user.id).count()
        total_storage = db.session.query(db.func.sum(Image.file_size)).filter_by(user_id=user.id).scalar() or 0
        
        user_stats.append({
            'user': user,
            'image_count': image_count,
            'storage_mb': round(total_storage / (1024 * 1024), 2)
        })
    
    return render_template('admin/users.html', user_stats=user_stats)


@app.route('/admin/images')
@admin_required
def admin_images():
    """Admin image management page"""
    images = Image.query.order_by(Image.uploaded_at.desc()).all()
    return render_template('admin/images.html', images=images)


@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Delete a user (admin only)"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/delete-image/<int:image_id>', methods=['POST'])
@admin_required
def admin_delete_image(image_id):
    """Delete an image (admin only)"""
    image = Image.query.get_or_404(image_id)
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    db.session.delete(image)
    db.session.commit()
    
    flash(f'Image "{image.title}" has been deleted.', 'success')
    return redirect(url_for('admin_images'))


@app.route('/admin/toggle-admin/<int:user_id>', methods=['POST'])
@admin_required
def admin_toggle_admin(user_id):
    """Toggle admin status of a user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot change your own admin status.', 'danger')
        return redirect(url_for('admin_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} for {user.username}.', 'success')
    return redirect(url_for('admin_users'))


# ==================== EXPORT ROUTES ====================

@app.route('/export/my-data/csv')
@login_required
def export_my_data_csv():
    """Export user's data as CSV"""
    csv_data = generate_user_data_csv(current_user)
    
    output = BytesIO()
    output.write(csv_data.encode('utf-8'))
    output.seek(0)
    
    filename = f"bhv_my_data_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@app.route('/export/my-data/json')
@login_required
def export_my_data_json():
    """Export user's data as JSON"""
    json_data = generate_user_data_json(current_user)
    
    output = BytesIO()
    output.write(json_data.encode('utf-8'))
    output.seek(0)
    
    filename = f"bhv_my_data_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.json"
    
    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )


@app.route('/admin/export/users')
@admin_required
def admin_export_users():
    """Export all users data as CSV (admin only)"""
    csv_data = generate_admin_users_csv()
    
    output = BytesIO()
    output.write(csv_data.encode('utf-8'))
    output.seek(0)
    
    filename = f"bhv_all_users_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@app.route('/admin/export/images')
@admin_required
def admin_export_images():
    """Export all images data as CSV (admin only)"""
    csv_data = generate_admin_images_csv()
    
    output = BytesIO()
    output.write(csv_data.encode('utf-8'))
    output.seek(0)
    
    filename = f"bhv_all_images_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


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


# ==================== HEALTH CHECK ====================

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat()
    })


# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        admins = [
            ('yadavchiragg', 'yadav@bhv.com', 'Demo2024!'),
            ('pradeeban', 'pradeeban@bhv.com', 'BHV2024!'),
            ('mdxabu', 'mdxabu@bhv.com', 'BHV2024!')
        ]
        
        for username, email, password in admins:
            if not User.query.filter_by(username=username).first():
                admin = User(username=username, email=email, is_admin=True)
                admin.set_password(password)
                db.session.add(admin)
        
        db.session.commit()
        print("Database initialized with admin accounts")
    
    app.run(debug=True, host='0.0.0.0', port=5000)