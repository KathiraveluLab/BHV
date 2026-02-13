"""
Admin Dashboard Routes
Provides admin functionality for user and image management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from bhv.app import db, User, Image
from pathlib import Path
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You need administrator privileges to access this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    """Main admin dashboard"""
    # Get statistics
    total_users = User.query.count()
    total_images = Image.query.count()
    
    # Calculate total storage used
    total_storage = db.session.query(db.func.sum(Image.file_size)).scalar() or 0
    total_storage_mb = round(total_storage / (1024 * 1024), 2)
    
    # Get recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Get recent images
    recent_images = Image.query.order_by(Image.uploaded_at.desc()).limit(10).all()
    
    # Get user with most uploads
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

@admin_bp.route('/users')
@admin_required
def users():
    """View all users"""
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

@admin_bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """View specific user details"""
    user = User.query.get_or_404(user_id)
    user_images = Image.query.filter_by(user_id=user_id).order_by(Image.uploaded_at.desc()).all()
    
    total_storage = db.session.query(db.func.sum(Image.file_size)).filter_by(user_id=user_id).scalar() or 0
    total_storage_mb = round(total_storage / (1024 * 1024), 2)
    
    return render_template('admin/user_detail.html', 
                         user=user, 
                         images=user_images,
                         total_storage_mb=total_storage_mb)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user and all their images"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('admin.users'))
    
    # Delete all user's image files
    for image in user.images:
        try:
            image_path = Path('static/uploads') / image.filename
            if image_path.exists():
                os.remove(image_path)
        except Exception as e:
            print(f"Error deleting file {image.filename}: {e}")
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} and all their images have been deleted.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/images')
@admin_required
def images():
    """View all images"""
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

@admin_bp.route('/images/<int:image_id>/delete', methods=['POST'])
@admin_required
def delete_image(image_id):
    """Delete an image"""
    image = Image.query.get_or_404(image_id)
    
    # Delete file from disk
    try:
        image_path = Path('static/uploads') / image.filename
        if image_path.exists():
            os.remove(image_path)
    except Exception as e:
        flash(f'Error deleting file: {e}', 'error')
        return redirect(url_for('admin.images'))
    
    image_title = image.title
    db.session.delete(image)
    db.session.commit()
    
    flash(f'Image "{image_title}" has been deleted.', 'success')
    return redirect(url_for('admin.images'))

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent removing your own admin status
    if user.id == current_user.id:
        flash('You cannot change your own admin status!', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = "granted" if user.is_admin else "revoked"
    flash(f'Admin privileges {status} for {user.username}.', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))