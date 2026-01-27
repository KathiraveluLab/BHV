from flask import Blueprint, jsonify, request
from backend.models import db, User, Image
from backend.middleware import token_required
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'message': 'Admin privileges required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats(current_user):
    user_count = User.query.count()
    image_count = Image.query.count()
    return jsonify({
        'user_count': user_count,
        'image_count': image_count
    }), 200

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users(current_user):
    search_query = request.args.get('search', '')
    if search_query:
        users = User.query.filter(User.email.ilike(f'%{search_query}%')).all()
    else:
        users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(current_user, user_id):
    if user_id == current_user.id:
        return jsonify({'message': 'Cannot delete yourself'}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    try:
        Image.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting user', 'error': str(e)}), 500

@admin_bp.route('/images/<int:image_id>', methods=['DELETE'])
@admin_required
def delete_image(current_user, image_id):
    image = Image.query.get(image_id)
    if not image:
        return jsonify({'message': 'Image not found'}), 404
        
    try:
        db.session.delete(image)
        db.session.commit()
        return jsonify({'message': 'Image deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting image', 'error': str(e)}), 500
