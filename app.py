from database import close_db
from flask import Flask, jsonify, render_template
import atexit
import os
import secrets

from dotenv import load_dotenv
from flask_login import LoginManager

load_dotenv()


def create_app():
    app = Flask(__name__)

    is_debug = os.environ.get(
        "FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        if is_debug:
            secret_key = secrets.token_urlsafe(32)
        else:
            raise RuntimeError(
                "SECRET_KEY environment variable must be set in production.")
    app.config["SECRET_KEY"] = secret_key
    app.config["DEBUG"] = is_debug

    login_manager = LoginManager()
    setattr(login_manager, "login_view", "auth.login")
    login_manager.init_app(app)

    from auth import AuthUser
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        user = User.get_by_id(user_id)
        if not user:
            return None
        return AuthUser(user)

    from auth import auth
    app.register_blueprint(auth)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    atexit.register(close_db)

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(port=port)
