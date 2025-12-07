"""Initialize database with tables."""
import sys
import os

# Add parent directory to path so we can import bhv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from bhv.database import db, init_db
from bhv.models import User, Image, Narrative, AuditLog

def create_app():
    """Create Flask app for database initialization."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bhv.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_db(app)
    return app

if __name__ == '__main__':
    print("Initializing BHV database...")
    app = create_app()
    print("✓ Database initialized successfully!")
    print("✓ Tables created:")
    print("  - users")
    print("  - images")
    print("  - narratives")
    print("  - audit_logs")
    print("\nDatabase file: bhv.db")
