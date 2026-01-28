import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from models import Image, User
from decorators import admin_required, login_required
from github_utils import GithubStorage

admin_upload_bp = Blueprint('admin_upload', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_upload_bp.route('/admin/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():
    if request.method == 'POST':
        file = request.files.get('file')
        target_user_id = request.form.get('target_user_id') 
        target_username = request.form.get('target_username')
        
        description = request.form.get('description', '').strip()
        sentiment = request.form.get('sentiment')
        ai_desc = request.form.get('ai_description', 'Admin Uploaded')

        if not file or not target_user_id:
            flash("Missing file or target user selection.", "warning")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("File type not supported.", "danger")
            return redirect(request.url)

        try:
            
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            file_content = file.read()
            file_size = len(file_content)

            if file_size > MAX_FILE_SIZE:
                flash("File exceeds Admin limit (10MB).", "danger")
                return redirect(request.url)

            
            github_url = GithubStorage.upload_file(
                repo_name=target_username, 
                file_content=file_content, 
                filename=unique_filename,
                user_id=target_user_id  
            )

            if not github_url:
                flash("GitHub upload failed.", "danger")
                return redirect(request.url)

            success = Image.save_metadata(
                user_id=target_user_id,
                username=target_username,
                uploader_role="Admin",        
                uploaded_by=session['user_id'], 
                uploader_name=f"Admin: {session.get('name')}",
                filename=unique_filename,
                github_url=github_url,
                description=description,
                sentiment=sentiment,
                ai_description=ai_desc,
                file_size=file_size,
                file_type=file.content_type,
                is_verified=True
            )

            if success:
                flash(f"Successfully uploaded to GitHub for {target_username}", "success")
            else:
                flash("Database error occurred.", "danger")
                
            return redirect(url_for('admin_upload.admin_dashboard'))

        except Exception as e:
            flash(f"Admin upload failed: {str(e)}", "danger")

    # GET request
    all_images = Image.get_all_images_admin()
    all_users = User.get_all_users() 
    return render_template('admin_upload.html', images=all_images, users=all_users)

@admin_upload_bp.route('/admin/delete/<upload_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_image(upload_id):
    image = Image.get_image_by_id(upload_id)
    if not image:
        flash("Image not found.", "danger")
        return redirect(url_for('admin_upload.admin_dashboard'))

    
    repo_name = image.get('username')
    filename = image.get('filename')
    owner_id = image.get('user_id') 

    
    github_deleted = GithubStorage.delete_file(repo_name, filename, user_id=owner_id)

    if github_deleted:
        
        Image.hard_delete(upload_id)
        flash("Image permanently deleted by admin.", "success")
    else:
        
        flash("Failed to delete from GitHub. The repo or file might not exist.", "danger")
        
    return redirect(url_for('admin_upload.admin_dashboard'))
@admin_upload_bp.route('/admin/edit/<upload_id>', methods=['POST'])
@login_required
@admin_required
def admin_edit_image(upload_id):
    new_desc = request.form.get('description', '').strip()
    new_sentiment = request.form.get('sentiment')
    new_ai_desc = request.form.get('ai_description', '').strip()

    success = Image.update_image_data(
        upload_id=upload_id,
        modifier_id=session['user_id'],
        modifier_name=f"Admin: {session.get('name')}",
        new_desc=new_desc,
        new_sentiment=new_sentiment,
        new_ai_desc=new_ai_desc
    )

    if success:
        flash("Image metadata updated successfully.", "success")
    else:
        flash("No changes made or error occurred.", "info")

    return redirect(url_for('admin_upload.admin_dashboard'))