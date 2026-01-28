from flask import Blueprint, render_template, session, redirect, url_for
from decorators import login_required, admin_required
from database import Database
from models import User , Image

dash_bp = Blueprint('dash', __name__)

@dash_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')

    if not user_id:
        session.clear()
        return render_template('errors/404.html'), 404

    user_data = User.find_by_id(user_id)
    if not user_data:
        session.clear()
        return render_template('errors/404.html'), 404

    images = Image.get_user_images(user_id) or []

    return render_template(
        'user_dashboard.html',
        user=user_data,
        images=images
    )


@dash_bp.route('/admin_dashboard')
@login_required
@admin_required
def admin_dashboard():
    all_users = list(User.get_all_users())

    all_images = Image.get_all_images_admin() or []

    admin_info = {
        "name": session.get('name'),
        "role": session.get('role')
    }

    return render_template(
        'admin_dashboard.html',
        admin=admin_info,
        users=all_users,
        images=all_images
    )