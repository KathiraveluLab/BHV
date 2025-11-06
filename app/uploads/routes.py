"""Upload routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import current_user
from bson import ObjectId
from app.uploads.forms import UploadForm
from app.models import Upload
from app.extensions import fs, db
from app.sentiment import analyze_sentiment
from app.utils import allowed_file
from app.config import Config
from app.auth.decorators import user_only, verified_user_required

uploads_bp = Blueprint('uploads', __name__)


@uploads_bp.route('/upload', methods=['GET', 'POST'])
@user_only
def upload():
    """Content upload route."""
    form = UploadForm()
    
    if form.validate_on_submit():
        try:
            # Get image file
            image_file = form.image.data
            if not image_file:
                flash('Image is required.', 'error')
                return render_template('uploads/upload.html', form=form)
            
            # Save image to GridFS
            image_id = fs.put(
                image_file,
                filename=image_file.filename,
                content_type=image_file.content_type
            )
            
            # Save audio file if provided
            audio_id = None
            if form.audio.data:
                audio_file = form.audio.data
                audio_id = fs.put(
                    audio_file,
                    filename=audio_file.filename,
                    content_type=audio_file.content_type
                )
            
            # Analyze sentiment
            sentiment_result = analyze_sentiment(form.description.data)
            sentiment_label = sentiment_result['label']
            
            # Create upload record
            upload_id = Upload.create(
                user_id=current_user.id,
                title=form.title.data,
                description=form.description.data,
                sentiment=sentiment_label,
                image_file_id=image_id,
                audio_file_id=audio_id
            )
            
            flash(f'Upload successful! Sentiment: {sentiment_label.capitalize()}', 'success')
            return redirect(url_for('uploads.detail', upload_id=upload_id))
            
        except Exception as e:
            flash(f'Upload failed: {str(e)}', 'error')
    
    return render_template('uploads/upload.html', form=form)


@uploads_bp.route('/gallery')
@user_only
def gallery():
    """Gallery view showing all uploads."""
    uploads = Upload.find_all()
    
    # Convert ObjectIds to strings for template
    uploads_list = []
    for upload in uploads:
        upload['_id'] = str(upload['_id'])
        upload['image_url'] = url_for('uploads.get_image', file_id=str(upload['image_file_id']))
        uploads_list.append(upload)
    
    return render_template('uploads/gallery.html', uploads=uploads_list)


@uploads_bp.route('/detail/<upload_id>')
@user_only
def detail(upload_id):
    """Detail view for a specific upload."""
    upload = Upload.find_by_id(upload_id)
    
    if not upload:
        flash('Upload not found.', 'error')
        return redirect(url_for('uploads.gallery'))
    
    upload['_id'] = str(upload['_id'])
    upload['image_url'] = url_for('uploads.get_image', file_id=str(upload['image_file_id']))
    
    if upload.get('audio_file_id'):
        upload['audio_url'] = url_for('uploads.get_audio', file_id=str(upload['audio_file_id']))
    
    return render_template('uploads/detail.html', upload=upload)


@uploads_bp.route('/file/image/<file_id>')
@verified_user_required
def get_image(file_id):
    """Serve image file from GridFS. Accessible by both users and admins for viewing."""
    try:
        grid_file = fs.get(ObjectId(file_id))
        return send_file(
            grid_file,
            mimetype=grid_file.content_type,
            download_name=grid_file.filename
        )
    except Exception as e:
        flash(f'Error loading image: {str(e)}', 'error')
        # Redirect appropriately based on user role
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('uploads.gallery'))


@uploads_bp.route('/file/audio/<file_id>')
@verified_user_required
def get_audio(file_id):
    """Serve audio file from GridFS. Accessible by both users and admins for viewing."""
    try:
        grid_file = fs.get(ObjectId(file_id))
        return send_file(
            grid_file,
            mimetype=grid_file.content_type,
            download_name=grid_file.filename
        )
    except Exception as e:
        flash(f'Error loading audio: {str(e)}', 'error')
        # Redirect appropriately based on user role
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('uploads.gallery'))

