"""Chat routes for AJAX-based messaging."""
from flask import Blueprint, request, jsonify
from flask_login import current_user
from app.models import ChatMessage, User
from app.auth.decorators import admin_required, verified_user_required

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/send', methods=['POST'])
@verified_user_required
def send_message():
    """Send a chat message."""
    data = request.get_json()
    message_text = data.get('message', '').strip()
    user_id = data.get('user_id', current_user.id)
    
    # Only admin can send messages to other users
    if user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not message_text:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Determine sender role
    sender_role = 'admin' if current_user.role == 'admin' else 'user'
    
    # Create message
    message_id = ChatMessage.create(user_id, message_text, sender_role)
    
    return jsonify({
        'success': True,
        'message_id': message_id,
        'message': message_text,
        'sender_role': sender_role
    })


@chat_bp.route('/list/<user_id>')
@verified_user_required
def list_messages(user_id):
    """Get chat messages for a user."""
    # Users can only see their own messages unless they're admin
    if user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    messages = ChatMessage.find_by_user(user_id)
    
    # Convert to JSON-serializable format
    messages_list = []
    for msg in messages:
        messages_list.append({
            'id': str(msg['_id']),
            'message': msg['message'],
            'sender_role': msg['sender_role'],
            'created_at': msg['created_at'].isoformat()
        })
    
    return jsonify({'messages': messages_list})


@chat_bp.route('/list')
@admin_required
def list_all_messages():
    """Get all chat messages (admin only)."""
    
    messages = ChatMessage.find_all()
    
    # Convert to JSON-serializable format
    messages_list = []
    for msg in messages:
        messages_list.append({
            'id': str(msg['_id']),
            'user_id': msg['user_id'],
            'message': msg['message'],
            'sender_role': msg['sender_role'],
            'created_at': msg['created_at'].isoformat()
        })
    
    return jsonify({'messages': messages_list})

