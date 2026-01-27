from flask import Flask
from flask_cors import CORS
from backend.config import Config
from backend.models import db
from backend.routes.auth import auth_bp
from backend.routes.images import images_bp
from backend.routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(images_bp, url_prefix='/images')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
