"""Flask application factory for BHV."""
from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, mail, init_mongodb
from app.models import User


@login_manager.user_loader
def load_user(user_id):
    """Load user from session."""
    return User.find_by_id(user_id)


def create_app(config_class=Config):
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure mail configuration is explicitly set (fix for .env loading issues)
    app.config['MAIL_SERVER'] = config_class.MAIL_SERVER
    app.config['MAIL_PORT'] = config_class.MAIL_PORT
    app.config['MAIL_USE_TLS'] = config_class.MAIL_USE_TLS
    app.config['MAIL_USERNAME'] = config_class.MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = config_class.MAIL_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = config_class.MAIL_DEFAULT_SENDER
    
    # Additional mail settings
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEBUG'] = app.debug
    
    # Initialize MongoDB
    init_mongodb(app)
    
    # Initialize extensions
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Initialize OAuth
    from app.auth.routes import init_oauth
    init_oauth(app)
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.uploads.routes import uploads_bp
    from app.admin.routes import admin_bp
    from app.chat.routes import chat_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(uploads_bp, url_prefix='/uploads')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    
    # Register index route
    from app.utils import index_route
    app.add_url_rule('/', 'index', index_route)
    
    return app

