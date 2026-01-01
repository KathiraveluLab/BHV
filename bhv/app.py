import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, Email
from werkzeug.utils import secure_filename
import uuid

db = SQLAlchemy()

# ==================== MODELS ====================

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    images = db.relationship('Image', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(50))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

# ==================== FORMS ====================

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password')
    ])
    
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    submit = SubmitField('Login')

class ImageUploadForm(FlaskForm):
    image = FileField('Image', validators=[
        FileRequired(message='Please select an image'),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=3, max=200, message='Title must be between 3 and 200 characters')
    ])
    
    description = TextAreaField('Description (Your Story)', validators=[
        Optional(),
        Length(max=5000, message='Description must be less than 5000 characters')
    ])
    
    submit = SubmitField('Upload Image')

# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def sanitize_filename(filename):
    filename = secure_filename(filename)
    filename = filename.replace('/', '').replace('\\', '')
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    return f"{name}{ext}"

def generate_unique_filename(original_filename):
    ext = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return unique_name

def validate_file_size(file_size, max_size):
    return 0 < file_size <= max_size

def get_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0

# ==================== APP FACTORY ====================

def create_app():
    BASE_DIR = Path(__file__).parent.parent
    
    app = Flask(__name__, 
                static_folder=str(BASE_DIR / 'static'),
                static_url_path='/static')
    
    # app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{BASE_DIR / "bhv.db"}'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['UPLOAD_FOLDER'] = BASE_DIR / 'static' / 'uploads'
    # app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    # app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'error'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        db.create_all()
    
    # ==================== PUBLIC ROUTES ====================
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/gallery')
    def gallery():
        images = Image.query.order_by(Image.uploaded_at.desc()).all()
        return render_template('gallery.html', images=images)
    
    @app.route('/uploads/<filename>')
    def serve_upload(filename):
        upload_folder = Path(app.config['UPLOAD_FOLDER'])
        return send_file(upload_folder / filename)
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'BHV'}), 200
    
    # ==================== AUTH ROUTES ====================
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = RegistrationForm()
        
        if form.validate_on_submit():
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'error')
                return redirect(url_for('register'))
            
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('Email already registered. Please use a different email.', 'error')
                return redirect(url_for('register'))
            
            if form.password.data != form.confirm_password.data:
                flash('Passwords do not match.', 'error')
                return redirect(url_for('register'))
            
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Welcome {user.username}! Your account has been created.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', form=form)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = LoginForm()
        
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user)
                flash(f'Welcome back, {user.username}!', 'success')
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Invalid username or password. Please try again.', 'error')
                return redirect(url_for('login'))
        
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        username = current_user.username
        logout_user()
        flash(f'Goodbye, {username}! You have been logged out.', 'success')
        return redirect(url_for('index'))
    
    @app.route('/profile')
    @login_required
    def profile():
        user_images = Image.query.filter_by(user_id=current_user.id).order_by(Image.uploaded_at.desc()).all()
        return render_template('profile.html', user=current_user, images=user_images)
    
    # ==================== UPLOAD ROUTES ====================
    
    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload():
        form = ImageUploadForm()
        
        if form.validate_on_submit():
            file = form.image.data
            
            if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
                flash('Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.', 'error')
                return redirect(request.url)
            
            original_filename = sanitize_filename(file.filename)
            unique_filename = generate_unique_filename(original_filename)
            file_path = Path(app.config['UPLOAD_FOLDER']) / unique_filename
            file.save(file_path)
            
            if not os.path.exists(file_path):
                flash('Failed to save file.', 'error')
                return redirect(request.url)
            
            file_size = get_file_size(file_path)
            if not validate_file_size(file_size, app.config['MAX_CONTENT_LENGTH']):
                os.remove(file_path)
                flash(f'File too large. Maximum size is 5MB.', 'error')
                return redirect(request.url)
            
            image = Image(
                filename=unique_filename,
                original_filename=original_filename,
                title=form.title.data,
                description=form.description.data,
                file_size=file_size,
                mime_type='image/jpeg',
                width=0,
                height=0,
                user_id=current_user.id
            )
            
            db.session.add(image)
            db.session.commit()
            
            flash('Image uploaded successfully!', 'success')
            return redirect(url_for('profile'))
        
        return render_template('upload.html', form=form)
    
    # ==================== ADMIN ROUTES ====================
    
    from functools import wraps
    
    def admin_required(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin:
                flash('You need administrator privileges to access this page.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        total_users = User.query.count()
        total_images = Image.query.count()
        
        total_storage = db.session.query(db.func.sum(Image.file_size)).scalar() or 0
        total_storage_mb = round(total_storage / (1024 * 1024), 2)
        
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_images = Image.query.order_by(Image.uploaded_at.desc()).limit(10).all()
        
        top_uploaders = db.session.query(
            User, db.func.count(Image.id).label('upload_count')
        ).join(Image).group_by(User.id).order_by(db.text('upload_count DESC')).limit(5).all()
        
        return render_template('admin/dashboard.html',
                             total_users=total_users,
                             total_images=total_images,
                             total_storage_mb=total_storage_mb,
                             recent_users=recent_users,
                             recent_images=recent_images,
                             top_uploaders=top_uploaders)
    
    @app.route('/admin/users')
    @admin_required
    def admin_users():
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.username.like(f'%{search}%'),
                    User.email.like(f'%{search}%')
                )
            )
        
        users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
        
        return render_template('admin/users.html', users=users, search=search)
    
    @app.route('/admin/users/<int:user_id>')
    @admin_required
    def admin_user_detail(user_id):
        user = User.query.get_or_404(user_id)
        user_images = Image.query.filter_by(user_id=user_id).order_by(Image.uploaded_at.desc()).all()
        
        total_storage = db.session.query(db.func.sum(Image.file_size)).filter_by(user_id=user_id).scalar() or 0
        total_storage_mb = round(total_storage / (1024 * 1024), 2)
        
        return render_template('admin/user_detail.html', 
                             user=user, 
                             images=user_images,
                             total_storage_mb=total_storage_mb)
    
    @app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
    @admin_required
    def admin_delete_user(user_id):
        user = User.query.get_or_404(user_id)
        
        if user.id == current_user.id:
            flash('You cannot delete your own account!', 'error')
            return redirect(url_for('admin_users'))
        
        for image in user.images:
            try:
                image_path = Path(app.config['UPLOAD_FOLDER']) / image.filename
                if image_path.exists():
                    os.remove(image_path)
            except Exception as e:
                print(f"Error deleting file {image.filename}: {e}")
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {username} and all their images have been deleted.', 'success')
        return redirect(url_for('admin_users'))
    
    @app.route('/admin/images')
    @admin_required
    def admin_images():
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        
        query = Image.query
        
        if search:
            query = query.filter(
                db.or_(
                    Image.title.like(f'%{search}%'),
                    Image.description.like(f'%{search}%')
                )
            )
        
        images = query.order_by(Image.uploaded_at.desc()).paginate(page=page, per_page=24, error_out=False)
        
        return render_template('admin/images.html', images=images, search=search)
    
    @app.route('/admin/images/<int:image_id>/delete', methods=['POST'])
    @admin_required
    def admin_delete_image(image_id):
        image = Image.query.get_or_404(image_id)
        
        try:
            image_path = Path(app.config['UPLOAD_FOLDER']) / image.filename
            if image_path.exists():
                os.remove(image_path)
        except Exception as e:
            flash(f'Error deleting file: {e}', 'error')
            return redirect(url_for('admin_images'))
        
        image_title = image.title
        db.session.delete(image)
        db.session.commit()
        
        flash(f'Image "{image_title}" has been deleted.', 'success')
        return redirect(url_for('admin_images'))
    
    @app.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
    @admin_required
    def admin_toggle_admin(user_id):
        user = User.query.get_or_404(user_id)
        
        if user.id == current_user.id:
            flash('You cannot change your own admin status!', 'error')
            return redirect(url_for('admin_users'))
        
        user.is_admin = not user.is_admin
        db.session.commit()
        
        status = "granted" if user.is_admin else "revoked"
        flash(f'Admin privileges {status} for {user.username}.', 'success')
        return redirect(url_for('admin_user_detail', user_id=user_id))
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)