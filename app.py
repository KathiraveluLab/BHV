import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Record

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'bhv-dev-fallback-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bhv.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email address is already in use')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    records = Record.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', records=records)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'image' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['image']
    narrative = request.form.get('narrative')
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
        
    if file:
        filename = secure_filename(file.filename)
        # Prefix with user ID and UUID for isolation and uniqueness
        filename = f"{current_user.id}_{uuid.uuid4().hex}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        new_record = Record(user_id=current_user.id, image_filename=filename, narrative=narrative)
        db.session.add(new_record)
        db.session.commit()
        flash('Record uploaded successfully')
        return redirect(url_for('dashboard'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return "Access Denied", 403
    all_records = Record.query.all()
    return render_template('admin.html', records=all_records)

@app.route('/record/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    if not current_user.is_admin:
        return "Access Denied", 403
    record = Record.query.get_or_404(record_id)
    # Delete from filesystem
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], record.image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        flash(f'Error deleting file: {e}')
        
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted successfully')
    return redirect(url_for('admin'))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    record = Record.query.filter_by(image_filename=filename).first_or_404()
    # Security: Ensure patients can only see their own files, unless they are admin
    if not current_user.is_admin and record.user_id != current_user.id:
        return "Access Denied", 403
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Initialize DB ---
with app.app_context():
    db.create_all()
    # Create default admin if not exists
    if not User.query.filter_by(username='admin').first():
        admin_password = os.environ.get('ADMIN_PASSWORD', 'bhv-admin-fallback-password')
        admin_user = User(
            username='admin', 
            email='admin@bhv.org', 
            password=generate_password_hash(admin_password),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
