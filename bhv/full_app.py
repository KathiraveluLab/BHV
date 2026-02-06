import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .db import init_db, create_user, get_user_by_email, create_entry, list_entries_for_patient, list_all_entries, get_entry, delete_entry, update_entry
from .storage.git_adapter import GitAdapter
import difflib

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def create_app(testing: bool = False, upload_folder: str = None):
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
    # allow tests or callers to override upload folder
    chosen_upload = upload_folder or UPLOAD_FOLDER
    app.config['UPLOAD_FOLDER'] = chosen_upload
    # testing config toggles
    if testing:
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
    # Allow overriding secure cookie behavior for local testing.
    # If SESSION_COOKIE_SECURE is set in the environment, honor it (1/true/yes = True).
    env_secure = os.environ.get('SESSION_COOKIE_SECURE')
    if env_secure is not None:
        app.config['SESSION_COOKIE_SECURE'] = str(env_secure).lower() in ('1', 'true', 'yes')
    else:
        app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # 7 days

    # Optional verbose request logging for debugging upload/CSRF issues.
    # Enable with `BHV_REQUEST_DEBUG=1`.
    app.config['REQUEST_DEBUG'] = str(os.environ.get('BHV_REQUEST_DEBUG', '')).lower() in ('1', 'true', 'yes')
    
    if app.config['REQUEST_DEBUG']:
        # Install a small WSGI middleware to log raw request headers and cookies
        # BEFORE other Flask before_request handlers (CSRFProtect registers a before_request).
        original_wsgi = app.wsgi_app

        def _logging_middleware(environ, start_response):
            try:
                method = environ.get('REQUEST_METHOD')
                path = environ.get('PATH_INFO', '')
                if method == 'POST' and path.startswith('/upload'):
                    print('---MW /upload START---')
                    # print some useful request metadata available at WSGI level
                    print('REQUEST_METHOD:', method)
                    print('PATH_INFO:', path)
                    print('CONTENT_TYPE:', environ.get('CONTENT_TYPE'))
                    print('CONTENT_LENGTH:', environ.get('CONTENT_LENGTH'))
                    print('HTTP_COOKIE:', environ.get('HTTP_COOKIE'))
                    # print a few header-like env vars
                    for k, v in environ.items():
                        if k.startswith('HTTP_'):
                            print(f"{k}: {v}")
                    print('---MW /upload END---')
            except Exception as _e:
                print('Logging middleware error:', _e)
            return original_wsgi(environ, start_response)

        app.wsgi_app = _logging_middleware
    csrf = CSRFProtect(app)
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    # Expose Google client id to templates so the Google Identity button gets the client id
    app.config['GOOGLE_CLIENT_ID'] = google_client_id or ''

    # init DB
    init_db()

    # storage adapter (use GitAdapter under uploads)
    storage = GitAdapter(app.config['UPLOAD_FOLDER'])


    def current_user():
        uid = session.get('user_email')
        if not uid:
            return None
        return get_user_by_email(uid)


    @app.route('/')
    def index():
        return render_template('home.html')


    @app.route('/dashboard')
    def dashboard():
        user = current_user()
        if not user:
            return redirect(url_for('login'))
        if user.get('role') == 'admin':
            return redirect(url_for('admin'))
        return redirect(url_for('my_entries'))


    @app.route('/features')
    def features():
        return render_template('features.html')


    @app.route('/how-it-works')
    def how_it_works():
        return render_template('how_it_works.html')


    @app.route('/testimonials')
    def testimonials():
        return render_template('testimonials.html')


    @app.route('/contact')
    def contact():
        return render_template('contact.html')


    @app.route('/profile')
    def profile():
        user = current_user()
        if not user:
            return redirect(url_for('login'))
        # fetch entries to display
        entries = list_entries_for_patient(user.get('email'))
        # TinyDB returns dicts, Mongo returns BSON; normalize attributes
        # For templates we expect e.filename, e.narrative, e.id (doc id)
        norm = []
        for e in entries:
            if isinstance(e, dict):
                # TinyDB uses 'doc_id' or returns as dict
                elem = type('E', (), {})()
                elem.filename = e.get('filename')
                elem.narrative = e.get('narrative')
                elem.id = e.get('doc_id') or e.get('_id')
            else:
                # pymongo returns mapping-like with attribute access not supported
                elem = type('E', (), {})()
                elem.filename = e.get('filename')
                elem.narrative = e.get('narrative')
                elem.id = str(e.get('_id')) if e.get('_id') else None
            norm.append(elem)
        return render_template('profile.html', user=user, entries=norm)


    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            email = request.form['email'].strip()
            password = request.form['password']
            if not is_valid_email(email):
                flash('Invalid email format')
                return redirect(url_for('signup'))
            if len(password) < 6:
                flash('Password must be at least 6 characters')
                return redirect(url_for('signup'))
            role = request.form.get('role', 'patient')
            if get_user_by_email(email):
                flash('User already exists')
                return redirect(url_for('signup'))
            pw = generate_password_hash(password)
            create_user(email, pw, role=role)
            session.permanent = True
            session['user_email'] = email
            return redirect(url_for('index'))
        return render_template('signup.html')


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email'].strip()
            password = request.form['password']
            user = get_user_by_email(email)
            if not user or not check_password_hash(user.get('password'), password):
                flash('Invalid email or password')
                return redirect(url_for('login'))
            session.permanent = True
            session['user_email'] = user.get('email')
            return redirect(url_for('index'))
        return render_template('login.html')


    @app.route('/logout')
    def logout():
        session.pop('user_email', None)
        return redirect(url_for('index'))


    @app.route('/auth/google', methods=['POST'])
    @csrf.exempt  # Google token in POST body, not CSRF token
    def auth_google():
        """Handle Google OAuth token from frontend (implicit/token flow)."""
        token = request.form.get('token') or request.json.get('token')
        if not token or not google_client_id:
            flash('Google authentication not configured')
            return redirect(url_for('login'))
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), google_client_id)
            email = idinfo.get('email')
            user = get_user_by_email(email)
            if not user:
                # Auto-create patient account on first Google login
                create_user(email, '', role='patient')  # empty password for OAuth
            session.permanent = True
            session['user_email'] = email
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Google login failed: {str(e)}')
            return redirect(url_for('login'))



    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        user = current_user()
        if not user:
            return redirect(url_for('login'))
        if request.method == 'POST':
            if app.config.get('REQUEST_DEBUG'):
                # DEBUG: print headers/cookies/form to help diagnose missing CSRF/session issues
                try:
                    print('---DEBUG /upload START---')
                    print('Request Headers:')
                    for k, v in request.headers.items():
                        print(f"{k}: {v}")
                    print('Request Cookies:')
                    for k, v in request.cookies.items():
                        print(f"{k}: {v}")
                    print('Form keys:', list(request.form.keys()))
                    print('---DEBUG /upload END---')
                except Exception as _e:
                    print('DEBUG logging failed:', _e)
            f = request.files.get('file')
            narrative = request.form.get('narrative', '')
            if not f:
                flash('File required')
                return redirect(url_for('upload'))
            filename = secure_filename(f.filename)
            patient_id = user.get('email') if user.get('role')=='patient' else request.form.get('patient_id')
            rel_path = os.path.join(patient_id, filename)
            data = f.read()
            # use storage adapter to save (creates commit)
            storage.save(rel_path, data, user_id=user.get('email'), action='upload')
            # record in DB
            create_entry(patient_id, filename, narrative)
            flash('Uploaded')
            return redirect(url_for('my_entries'))
        return render_template('upload.html')


    @app.route('/my')
    def my_entries():
        user = current_user()
        if not user:
            return redirect(url_for('login'))
        patient_id = user.get('email') if user.get('role')=='patient' else request.args.get('patient_id')
        entries = list_entries_for_patient(patient_id)
        return render_template('patient.html', entries=entries, patient_id=patient_id)


    @app.route('/admin')
    def admin():
        user = current_user()
        if not user or user.get('role')!='admin':
            return redirect(url_for('login'))
        entries = list_all_entries()
        return render_template('admin.html', entries=entries)


    @app.route('/uploads/<path:filename>')
    def uploads(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


    @app.route('/entry/<entry_id>/delete', methods=['POST'])
    def entry_delete(entry_id):
        user = current_user()
        if not user:
            return redirect(url_for('login'))
        delete_entry(entry_id)
        flash('Deleted')
        return redirect(url_for('admin') if user.get('role')=='admin' else url_for('my_entries'))


    @app.route('/history/<patient_id>/<filename>')
    def history(patient_id, filename):
        user = current_user()
        if not user:
            return redirect(url_for('login'))
        # basic access check: patients can view their own history; admins can view all
        if user.get('role') != 'admin' and user.get('email') != patient_id:
            flash('Forbidden')
            return redirect(url_for('index'))
        rel = os.path.join(patient_id, filename)
        commits = storage.history(rel)
        return render_template('history.html', commits=commits, patient_id=patient_id, filename=filename)


    @app.route('/diff/<patient_id>/<filename>/<old_sha>/<new_sha>')
    def diff(patient_id, filename, old_sha, new_sha):
        user = current_user()
        if not user:
            return redirect(url_for('login'))
        if user.get('role') != 'admin' and user.get('email') != patient_id:
            flash('Forbidden')
            return redirect(url_for('index'))
        rel = os.path.join(patient_id, filename)
        old_bytes = storage.get(rel, old_sha)
        new_bytes = storage.get(rel, new_sha)
        try:
            old_text = old_bytes.decode('utf-8').splitlines()
        except Exception:
            old_text = old_bytes.decode('latin-1', errors='ignore').splitlines()
        try:
            new_text = new_bytes.decode('utf-8').splitlines()
        except Exception:
            new_text = new_bytes.decode('latin-1', errors='ignore').splitlines()
        ud = difflib.unified_diff(old_text, new_text, fromfile=old_sha, tofile=new_sha, lineterm='')
        diff_text = '\n'.join(list(ud))
        return render_template('diff.html', diff=diff_text, patient_id=patient_id, filename=filename, old=old_sha, new=new_sha)


    @app.route('/file/<patient_id>/<filename>')
    @app.route('/file/<patient_id>/<filename>/<version>')
    def file_version(patient_id, filename, version=None):
        user = current_user()
        if not user:
            return redirect(url_for('login'))
        if user.get('role') != 'admin' and user.get('email') != patient_id:
            flash('Forbidden')
            return redirect(url_for('index'))
        rel = os.path.join(patient_id, filename)
        data = storage.get(rel, version)
        return Response(data, mimetype='application/octet-stream', headers={'Content-Disposition': f'attachment; filename="{filename}"'})


    return app
