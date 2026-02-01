import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_from_directory
from werkzeug.utils import secure_filename
from models import Image
from decorators import login_required
from github_utils import GithubStorage

user_upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_upload_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_page():
    if request.method == 'POST':
        file = request.files.get('file')
        description = request.form.get('description', '').strip()
        sentiment = request.form.get('sentiment')
        
        if not file or file.filename == '':
            flash("No file selected.", "warning")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Invalid file type.", "danger")
            return redirect(request.url)

        try:
            # 1. Define filenames and content first
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}" # Defined here
            
            file_content = file.read()
            file_size = len(file_content)

            if file_size > MAX_FILE_SIZE:
                flash("File size exceeds 5MB limit.", "danger")
                return redirect(request.url)

            # 2. Get User Info from session
            repo_display_name = session.get('name', 'General').strip()
            user_id = session.get('user_id')

            # 3. Upload to GitHub using the unique user_id
            github_url = GithubStorage.upload_file(
                repo_name=repo_display_name, 
                file_content=file_content, 
                filename=unique_filename,
                user_id=user_id # Ensures unique repo per person
            )

            if not github_url:
                flash("Failed to upload image to GitHub.", "danger")
                return redirect(request.url)
            
            # 4. Save to Database
            success = Image.save_metadata(
                user_id=user_id,
                username=repo_display_name,
                uploaded_by=user_id,
                uploader_name=repo_display_name,
                filename=unique_filename,
                github_url=github_url, 
                description=description,
                sentiment=sentiment,
                ai_description="", 
                file_size=file_size,
                file_type=file.content_type
            )
            
            if success:
                flash("Image stored on GitHub successfully.", "success")
            else:
                flash("Database error: Could not save image info.", "danger")
                
            return redirect(url_for('upload.upload_page'))
        
        except Exception as e:
            # This is where your error was being caught
            flash(f"An unexpected error occurred: {str(e)}", "danger")

    # GET request: Show images
    images = Image.get_user_images(session['user_id'])
    return render_template('user_upload.html', images=images)

@user_upload_bp.route('/delete/<upload_id>', methods=['POST'])
@login_required
def delete(upload_id):
    image = Image.get_image_by_id(upload_id)    
    if not image:
        flash("Image not found.", "danger")
        return redirect(url_for('dash.dashboard'))

    repo_name = image['username']
    user_id = image['user_id']
    filename = image['filename']

    
    github_deleted = GithubStorage.delete_file(repo_name, filename, user_id=user_id)

    if github_deleted:
        Image.hard_delete(upload_id)
        flash("Image permanently deleted from GitHub and Database.", "success")
    else:
        flash("Failed to delete image from GitHub. It may have been already removed or permissions may have changed.", "danger")

    return redirect(url_for('dash.dashboard'))

@user_upload_bp.route('/edit/<upload_id>', methods=['POST'])
@login_required
def edit_image(upload_id):
    image = Image.get_image_by_id(upload_id)
    if not image or image['user_id'] != session['user_id']:
        flash("Unauthorized or image not found.", "danger")
        return redirect(url_for('upload.upload_page'))

    new_desc = request.form.get('description', '').strip()
    new_sentiment = request.form.get('sentiment')

    success = Image.update_image_data(
        upload_id=upload_id,
        modifier_id=session['user_id'],
        modifier_name=session.get('name', 'User'),
        new_desc=new_desc,
        new_sentiment=new_sentiment
    )

    if success:
        flash("Metadata updated successfully.", "success")
    else:
        flash("No changes made.", "info")

    return redirect(url_for('upload.upload_page'))