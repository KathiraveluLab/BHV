
from .main_routes import main_bp
from .auth_routes import auth_bp
from .dash_routes import dash_bp
from .error_routes import errors_bp
from .user_upload_routes import user_upload_bp
from .admin_upload_routes import admin_upload_bp
from .admin_analysis_routes import admin_analysis_bp


def register_all_blueprints(app):
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dash_bp, url_prefix='/') 
    app.register_blueprint(errors_bp, url_prefix='/errors')
    app.register_blueprint(user_upload_bp)
    app.register_blueprint(admin_upload_bp)
    app.register_blueprint(admin_analysis_bp)