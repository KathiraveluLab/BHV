import atexit
import os
import secrets

from dotenv import load_dotenv
from flask import Flask, jsonify

from database import close_db


def create_app():
    load_dotenv()
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

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    atexit.register(close_db)

    return app


if __name__ == "__main__":
    app = create_app()
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(debug=debug, port=port)
