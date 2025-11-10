"""Flask extension initializations."""
from flask_login import LoginManager
from flask_mail import Mail
from pymongo import MongoClient
from gridfs import GridFS
from app.config import Config

# MongoDB connection
client = None
db = None
fs = None  # GridFS instance


def init_mongodb(app):
    """Initialize MongoDB connection and GridFS."""
    global client, db, fs
    client = MongoClient(app.config['MONGODB_URI'])
    db = client[app.config['MONGODB_DB']]
    fs = GridFS(db)


# Flask extensions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

mail = Mail()

# Additional mail settings that might be needed
def configure_mail_debug(app):
    """Configure mail debugging if needed."""
    if app.debug:
        import logging
        logging.getLogger('flask_mail').setLevel(logging.DEBUG)

