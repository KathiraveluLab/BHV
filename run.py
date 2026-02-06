"""Entry point to run the BHV minimalist monolith.

Usage: python run.py

It picks up `MONGO_URI` environment variable to use MongoDB; otherwise uses TinyDB.
"""
import os
from dotenv import load_dotenv

# Load environment variables from a .env file at project root (if present)
load_dotenv()

from bhv.full_app import create_app


def main():
    port = int(os.environ.get('PORT', 5000))
    app = create_app()
    # Respect FLASK_ENV to determine debug/reloader behavior
    flask_env = os.environ.get('FLASK_ENV', 'development')
    is_production = flask_env == 'production'
    # In production mode we explicitly disable the debugger and reloader
    app.run(host='0.0.0.0', port=port, debug=not is_production, use_reloader=not is_production)


if __name__ == '__main__':
    main()
