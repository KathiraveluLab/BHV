import os
import requests
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId

load_dotenv()

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'bhv_prototype'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_key_do_not_use_in_prod')  

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OAuth Setup
from authlib.integrations.flask_client import OAuth
oauth = OAuth(app)

oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MongoDB Setup
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
images_collection = db.images
users_collection = db.users

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data.get('username')
        self.email = user_data.get('email')

    @staticmethod
    def get(user_id):
        user_data = users_collection.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def find_by_username(username):
        user_data = users_collection.find_one({'username': username})
        if user_data:
            return User(user_data)
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_github_repo(access_token, username):
    repo_name = f"bhv-vault-{username}"
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
   
    check_url = f"https://api.github.com/repos/{username}/{repo_name}"
    resp = requests.get(check_url, headers=headers)
    
    if resp.status_code == 200:
        print(f" * Repository {repo_name} already exists.")
        return repo_name

    create_url = "https://api.github.com/user/repos"
    data = {
        "name": repo_name,
        "private": True,
        "description": "Behavioral Health Vault - Private User Data",
        "auto_init": True 
    }
    
    resp = requests.post(create_url, json=data, headers=headers)
    
    if resp.status_code == 201:
        print(f" * Successfully created private repository: {repo_name}")
        return repo_name
    else:
        print(f" ! Failed to create repository: {resp.status_code} - {resp.text}")
        return None

@app.route('/')
def index():
    images = list(images_collection.find().sort('timestamp', -1))
    return render_template('index.html', images=images, user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if users_collection.find_one({'username': username}):
            flash('Username already exists')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({
            'username': username,
            'password': hashed_password,
            'created_at': datetime.now()
        })
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = users_collection.find_one({'username': username})
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/login/github')
def login_github():
    redirect_uri = url_for('authorize_github', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@app.route('/login/github/callback')
def authorize_github():
    token = oauth.github.authorize_access_token()
    resp = oauth.github.get('user', token=token)
    user_info = resp.json()
    username = user_info['login']
    user_data = users_collection.find_one({'username': username})
    repo_name = create_github_repo(token['access_token'], username)
    
    if not user_data:
        users_collection.insert_one({
            'username': username,
            'oauth_provider': 'github',
            'github_repo': repo_name,
            'created_at': datetime.now()
        })
        user_data = users_collection.find_one({'username': username})
    elif repo_name and 'github_repo' not in user_data:
         users_collection.update_one({'_id': user_data['_id']}, {'$set': {'github_repo': repo_name}})
    
    user = User(user_data)
    login_user(user)
    return redirect(url_for('index'))

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorize_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def authorize_google():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    if not user_info:
        user_info = oauth.google.userinfo()
        
    email = user_info['email']
    username = email.split('@')[0]
    user_data = users_collection.find_one({'email': email})
    if not user_data:
        if users_collection.find_one({'username': username}):
            username = email

        users_collection.insert_one({
            'username': username,
            'email': email,
            'oauth_provider': 'google',
            'created_at': datetime.now()
        })
        user_data = users_collection.find_one({'email': email})
    
    user = User(user_data)
    login_user(user)
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    title = request.form.get('title')
    description = request.form.get('description')

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        image_data = {
            'filename': filename,
            'title': title,
            'description': description,
            'uploaded_by': current_user.username,
            'timestamp': datetime.now()
        }
        images_collection.insert_one(image_data)

    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print(f" * Database initialized: MongoDB ({DB_NAME})")
    print(f" * Upload folder: {UPLOAD_FOLDER}")
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1'), port=5001, host='0.0.0.0')
