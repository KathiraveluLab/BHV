"""Admin routes."""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user
from app.models import Upload, User
from app.auth.decorators import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard showing statistics."""
    # Get sentiment counts
    sentiment_counts = Upload.count_by_sentiment()
    
    # Get total counts
    total_uploads = Upload.get_total_count()
    from app.models import get_db
    total_users = get_db().users.count_documents({})
    
    # Get recent uploads
    recent_uploads = Upload.find_all(limit=10)
    for upload in recent_uploads:
        upload['_id'] = str(upload['_id'])
        upload['image_url'] = url_for('uploads.get_image', file_id=str(upload['image_file_id']))
    
    # Prepare chart data
    chart_data = {
        'labels': ['Positive', 'Neutral', 'Negative'],
        'data': [
            sentiment_counts.get('positive', 0),
            sentiment_counts.get('neutral', 0),
            sentiment_counts.get('negative', 0)
        ]
    }
    
    return render_template(
        'admin/dashboard.html',
        sentiment_counts=sentiment_counts,
        total_uploads=total_uploads,
        total_users=total_users,
        recent_uploads=recent_uploads,
        chart_data=chart_data
    )


@admin_bp.route('/all-uploads')
@admin_required
def all_uploads():
    """View all uploads (admin only)."""
    uploads = Upload.find_all()
    
    # Convert ObjectIds to strings for template
    uploads_list = []
    for upload in uploads:
        upload['_id'] = str(upload['_id'])
        upload['image_url'] = url_for('uploads.get_image', file_id=str(upload['image_file_id']))
        uploads_list.append(upload)
    
    return render_template('uploads/gallery.html', uploads=uploads_list, admin_view=True)


@admin_bp.route('/users')
@admin_required
def users():
    """View all users (admin only)."""
    from app.models import get_db
    from bson import ObjectId
    
    users_list = list(get_db().users.find().sort('created_at', -1))
    
    # Process users data
    users_data = []
    for user in users_list:
        user['_id'] = str(user['_id'])
        user['upload_count'] = get_db().uploads.count_documents({'user_id': user['_id']})
        user['chat_count'] = get_db().chat_messages.count_documents({'user_id': user['_id']})
        users_data.append(user)
    
    return render_template('admin/users.html', users=users_data)


@admin_bp.route('/user/<user_id>')
@admin_required
def user_detail(user_id):
    """View details of a specific user (admin only)."""
    from app.models import get_db
    from bson import ObjectId
    
    try:
        user_data = get_db().users.find_one({'_id': ObjectId(user_id)})
        if not user_data:
            flash('User not found.', 'error')
            return redirect(url_for('admin.users'))
        
        user_data['_id'] = str(user_data['_id'])
        
        # Get user's uploads
        user_uploads = list(get_db().uploads.find({'user_id': user_data['_id']}).sort('created_at', -1))
        for upload in user_uploads:
            upload['_id'] = str(upload['_id'])
            upload['image_url'] = url_for('uploads.get_image', file_id=str(upload['image_file_id']))
        
        # Get user's chat messages
        user_chats = list(get_db().chat_messages.find({'user_id': user_data['_id']}).sort('created_at', -1))
        for chat in user_chats:
            chat['_id'] = str(chat['_id'])
        
        return render_template('admin/user_detail.html', user=user_data, uploads=user_uploads, chats=user_chats)
    except Exception as e:
        flash(f'Error loading user: {str(e)}', 'error')
        return redirect(url_for('admin.users'))


@admin_bp.route('/chats')
@admin_required
def chats():
    """View all chats (admin only)."""
    from app.models import ChatMessage, get_db
    from bson import ObjectId
    
    # Get all chat messages grouped by user
    all_messages = ChatMessage.find_all()
    
    # Group messages by user_id
    users_chats = {}
    for msg in all_messages:
        user_id = msg['user_id']
        if user_id not in users_chats:
            # Get user info
            try:
                user_data = get_db().users.find_one({'_id': ObjectId(user_id)})
                if user_data:
                    users_chats[user_id] = {
                        'user': {
                            'id': str(user_data['_id']),
                            'email': user_data.get('email', 'Unknown'),
                            'created_at': user_data.get('created_at')
                        },
                        'messages': []
                    }
            except:
                users_chats[user_id] = {
                    'user': {
                        'id': user_id,
                        'email': 'Unknown',
                        'created_at': None
                    },
                    'messages': []
                }
        
        msg['_id'] = str(msg['_id'])
        users_chats[user_id]['messages'].append(msg)
    
    return render_template('admin/chats.html', users_chats=list(users_chats.values()))

