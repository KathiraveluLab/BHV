import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from backend.models import db, Image
from backend.middleware import token_required

images_bp = Blueprint('images', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@images_bp.route('/upload', methods=['POST'])
@token_required
def upload_image(current_user):
    if 'image' not in request.files:
        return jsonify({'message': 'No image part'}), 400
    
    file = request.files['image']
    description = request.form.get('description', '')

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file.save(filepath)
        
        new_image = Image(
            filename=unique_filename,
            description=description,
            user_id=current_user.id
        )
        
        db.session.add(new_image)
        db.session.commit()
        
        return jsonify({
            'message': 'Image uploaded successfully',
            'image': new_image.to_dict()
        }), 201
        
    return jsonify({'message': 'File type not allowed'}), 400

@images_bp.route('/', methods=['GET'])
@token_required
def get_images(current_user):
    user_id = request.args.get('user_id')
    search_query = request.args.get('search')
    
    query = Image.query
    
    if user_id:
        if user_id == 'me':
            query = query.filter_by(user_id=current_user.id)
        else:
            query = query.filter_by(user_id=user_id)
            
    if search_query:
        query = query.filter(
            (Image.description.ilike(f'%{search_query}%')) |
            (Image.filename.ilike(f'%{search_query}%'))
        )
            
    images = query.order_by(Image.uploaded_at.desc()).all()
    return jsonify([img.to_dict() for img in images]), 200

@images_bp.route('/file/<filename>', methods=['GET'])
def get_image_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
