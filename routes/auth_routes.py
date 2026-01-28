from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from decorators import login_required
from auth import AuthService
from models import User
from extensions import limiter, oauth 

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        
        user_info = AuthService.authenticate(email, password)
        
        if isinstance(user_info, dict) and user_info.get('error') == 'set_password_required':
            flash("This account is secured via Google. Please use Google Login.", "info")
            return redirect(url_for('auth.login'))

        if user_info:
            AuthService.login_user(user_info)
            flash(f"Welcome back, {user_info.get('name')}!", "success")
            return redirect(url_for('dash.admin_dashboard' if user_info.get('role') == 'admin' else 'dash.dashboard'))
                
        flash("Invalid email or password.", "danger")
    return render_template('login.html')

@auth_bp.route('/login/google')
def google_login():
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/login/google/callback')
def google_authorize():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        email = user_info.get('email').strip().lower()
        google_id = user_info['sub']

        if AuthService.is_system_admin(email):
            auth_payload = {
                "id": "SYSTEM_ADMIN_001",
                "name": user_info.get('name', "System Admin"),
                "role": "admin"
            }
            AuthService.login_user(auth_payload)
            flash("System Admin authenticated via Google.", "success")
            return redirect(url_for('dash.admin_dashboard'))

        user = User.find_by_google_id(google_id)
        if not user:
            user = User.find_by_email(email)
            if user:
                from database import Database
                db = Database.get_db()
                db.users.update_one({"email": email}, {"$set": {"google_id": google_id}})
                user = User.find_by_email(email)
            else:
                user = User.create_google_user(user_info.get('name'), email, google_id)

        AuthService.login_user({"id": user['user_id'], "name": user['name'], "role": user['role']})

        if not user.get('password'):
            flash("Identity verified. Please establish your Vault Security Key.", "info")
            return redirect(url_for('auth.setup_password'))

        return redirect(url_for('dash.dashboard'))

    except Exception as e:
        print(f"OAuth Admin Error: {str(e)}")
        flash("Google Authentication failed.", "danger")
        return redirect(url_for('auth.login'))

@auth_bp.route('/setup-password', methods=['GET', 'POST'])
@login_required
def setup_password():
    user = User.find_by_id(session.get('user_id'))
    if user and user.get('password'):
        return redirect(url_for('dash.dashboard'))

    if request.method == 'POST':
        pwd = request.form.get('password')
        conf = request.form.get('confirm_password')

        if not pwd or len(pwd) < 8:
            flash("Password must be 8+ characters.", "warning")
        elif pwd != conf:
            flash("Passwords do not match.", "danger")
        else:
            if User.set_password(session.get('user_id'), pwd):
                flash("Vault Key established!", "success")
                return redirect(url_for('dash.dashboard'))
                
    return render_template('setup_password.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
@limiter.limit("30 per hour")
def signup():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        if User.create_user(name, email, password):
            flash("Account created! Please log in.", "success")
            return redirect(url_for('auth.login'))
        flash("Email already exists.", "warning")
    return render_template('signup.html')

@auth_bp.route('/logout')
@login_required 
def logout():
    AuthService.logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))