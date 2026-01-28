from flask import Blueprint, render_template

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def handle_404(e):
    return render_template('errors/404.html'), 404

@errors_bp.app_errorhandler(429)
def handle_429(e):
    return render_template('errors/429.html'), 429

@errors_bp.app_errorhandler(500)
def handle_500(e):
    return render_template('errors/500.html'), 500