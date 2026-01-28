import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_talisman import Talisman
from dotenv import load_dotenv
from extensions import csrf, limiter, oauth
from routes import register_all_blueprints

load_dotenv()

def create_app():
    app = Flask(__name__)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')

    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("No SECRET_KEY set for Flask application.")
    app.secret_key = secret_key
    
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False if app.debug else True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['RATELIMIT_ENABLED'] = False
   
    csrf.init_app(app)
    limiter.init_app(app)
    oauth.init_app(app) 

    oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    
    csp = {
        'default-src': "'self'",
        
        
        'style-src': [
            "'self'", 
            "'unsafe-inline'", 
            "https://cdnjs.cloudflare.com", 
            "https://fonts.googleapis.com"
        ],
        
        
        'script-src': [
            "'self'", 
            "'unsafe-inline'", 
            "https://accounts.google.com", 
            "https://cdnjs.cloudflare.com",
            "https://cdn.jsdelivr.net"
        ],
        
        
        'frame-src': ["https://accounts.google.com"],
        
        
        'img-src': [
            "'self'", 
            "data:", 
            "https://raw.githubusercontent.com", 
            "https://github.com",
            "https://upload.wikimedia.org" 
        ],

        'font-src': [
            "'self'", 
            "https://cdnjs.cloudflare.com", 
            "https://fonts.gstatic.com"
        ]
    }

    Talisman(app, content_security_policy=csp, force_https=False)  

    register_all_blueprints(app)    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)