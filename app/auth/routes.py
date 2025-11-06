"""Authentication routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.auth.decorators import verified_user_required
from authlib.integrations.flask_client import OAuth
from flask_mail import Message
from app.auth.forms import RegisterForm, LoginForm, OTPVerifyForm
from app.models import User, OTP
from app.extensions import mail, db
from app.utils import generate_otp, find_or_create_user_google, send_email_direct_smtp
from app.config import Config

auth_bp = Blueprint('auth', __name__)

# OAuth instance (will be initialized in init_oauth)
oauth = None


def init_oauth(app):
    """Initialize Google OAuth."""
    global oauth
    oauth = OAuth(app)
    oauth.register(
        name='google',
        client_id=Config.GOOGLE_CLIENT_ID,
        client_secret=Config.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    return oauth


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route - creates user with is_verified=False and sends OTP for verification."""
    if current_user.is_authenticated:
        return redirect(url_for('uploads.gallery'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        
        # Check if user already exists and is verified
        existing_user = User.find_by_email(email)
        if existing_user and existing_user.is_verified:
            flash('Email is already registered and verified. Please login instead.', 'info')
            return redirect(url_for('auth.login'))
        
        # If user exists but not verified, update password and role, then resend OTP
        if existing_user and not existing_user.is_verified:
            # Update password in case it changed
            from app.models import get_db
            from bson import ObjectId
            import bcrypt
            from app.config import is_admin_email
            
            password_hash = bcrypt.hashpw(
                form.password.data.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Determine role based on ADMIN_EMAILS match
            role = 'admin' if is_admin_email(email) else 'user'
            
            # Update password and role
            get_db().users.update_one(
                {'_id': ObjectId(existing_user.id)},
                {'$set': {
                    'password_hash': password_hash,
                    'role': role  # Update role based on ADMIN_EMAILS check
                }}
            )
        else:
            # Create user immediately with is_verified=False (will be verified after OTP)
            # This avoids storing plain password in session
            user = User.create(
                email=email,
                password=form.password.data,
                role=None  # Let User.create() determine role from ADMIN_EMAILS
            )
        
        # Generate and send OTP
        otp_code = generate_otp()
        OTP.create(email, otp_code)
        
        # Send OTP email
        email_sent = False
        try:
            mail_username = current_app.config.get('MAIL_USERNAME')
            mail_password = current_app.config.get('MAIL_PASSWORD')
            
            if mail_username and mail_password:
                # Try Flask-Mail first
                try:
                    msg = Message(
                        subject='Verify your email - BHV',
                        recipients=[email],
                        body=f'Your OTP code is: {otp_code}\n\nThis code will expire in {Config.OTP_EXPIRY_MINUTES} minutes.'
                    )
                    mail.send(msg)
                    email_sent = True
                except Exception as mail_error:
                    # If Flask-Mail fails, try direct SMTP as fallback
                    current_app.logger.warning(f"Flask-Mail failed, trying direct SMTP: {str(mail_error)}")
                    success, error = send_email_direct_smtp(
                        email,
                        'Verify your email - BHV',
                        f'Your OTP code is: {otp_code}\n\nThis code will expire in {Config.OTP_EXPIRY_MINUTES} minutes.'
                    )
                    if success:
                        email_sent = True
                    else:
                        raise Exception(error)
            else:
                # Email not configured - log error
                current_app.logger.warning("Email not configured - OTP cannot be sent")
                email_sent = False
        except Exception as e:
            # Log email sending error
            error_msg = str(e)
            current_app.logger.error(f"Failed to send OTP email: {error_msg}")
            email_sent = False
        
        # Store only email in session (password is already hashed in database)
        session['pending_email'] = email
        
        if email_sent and (Config.MAIL_USERNAME and Config.MAIL_PASSWORD):
            flash('OTP has been sent to your email. Please verify your email.', 'success')
        else:
            flash('Failed to send OTP email. Please configure email settings or contact administrator.', 'error')
        return redirect(url_for('auth.verify_otp'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route - checks ADMIN_EMAILS on every login and updates role accordingly."""
    if current_user.is_authenticated:
        return redirect(url_for('uploads.gallery'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        
        if user and user.check_password(form.password.data):
            # Only require OTP verification if user hasn't been verified yet
            if not user.is_verified:
                flash('Please verify your email before logging in. Please register again to receive a new OTP.', 'warning')
                return redirect(url_for('auth.register'))
            
            # Check ADMIN_EMAILS on every login and update role accordingly
            from app.config import is_admin_email
            
            should_be_admin = is_admin_email(user.email)
            current_role_is_admin = (user.get_stored_role() == 'admin')
            
            # Update role in database if it doesn't match ADMIN_EMAILS check
            if should_be_admin and not current_role_is_admin:
                user.update_role('admin')
            elif not should_be_admin and current_role_is_admin:
                user.update_role('user')
            
            # User is verified, proceed with login
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('uploads.gallery'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """OTP verification route - verifies user email after successful OTP validation."""
    if current_user.is_authenticated:
        return redirect(url_for('uploads.gallery'))
    
    pending_email = session.get('pending_email')
    
    if not pending_email:
        flash('Please register first.', 'warning')
        return redirect(url_for('auth.register'))
    
    form = OTPVerifyForm()
    if form.validate_on_submit():
        otp_code = form.otp_code.data
        
        if OTP.find_valid(pending_email, otp_code):
            # Mark OTP as used
            OTP.mark_used(pending_email, otp_code)
            
            # Get user (should already exist from registration)
            user = User.find_by_email(pending_email)
            
            if not user:
                flash('User not found. Please register again.', 'error')
                session.pop('pending_email', None)
                return redirect(url_for('auth.register'))
            
            # Check and update role based on ADMIN_EMAILS match (in case it changed)
            from app.config import is_admin_email
            
            should_be_admin = is_admin_email(pending_email)
            current_role_is_admin = (user.get_stored_role() == 'admin')
            
            # Update role in database if it doesn't match ADMIN_EMAILS check
            if should_be_admin and not current_role_is_admin:
                user.update_role('admin')
            elif not should_be_admin and current_role_is_admin:
                user.update_role('user')
            
            # Verify user (user already exists with hashed password from registration)
            user.verify()
            
            # Login user
            login_user(user, remember=True)
            
            # Clear session data
            session.pop('pending_email', None)
            
            # Determine role for flash message
            role = 'admin' if is_admin_email(pending_email) else 'user'
            flash(f'Email verified successfully! Registered as {role}.', 'success')
            return redirect(url_for('uploads.gallery'))
        
        flash('Invalid or expired OTP code.', 'error')
    
    return render_template('auth/otp_verify.html', form=form)


@auth_bp.route('/google-login')
def google_login():
    """Initiate Google OAuth login."""
    if not Config.GOOGLE_CLIENT_ID or not Config.GOOGLE_CLIENT_SECRET:
        flash('Google OAuth is not configured.', 'error')
        return redirect(url_for('auth.login'))
    
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/google-callback')
def google_callback():
    """Handle Google OAuth callback - checks ADMIN_EMAILS on every login and updates role."""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            user_info = oauth.google.parse_id_token(token)
        
        user = find_or_create_user_google(user_info)
        
        # Check ADMIN_EMAILS on every login and update role accordingly
        from app.config import is_admin_email
        
        should_be_admin = is_admin_email(user.email)
        current_role_is_admin = (user.get_stored_role() == 'admin')
        
        # Update role in database if it doesn't match ADMIN_EMAILS check
        if should_be_admin and not current_role_is_admin:
            user.update_role('admin')
        elif not should_be_admin and current_role_is_admin:
            user.update_role('user')
        
        login_user(user, remember=True)
        flash('Logged in with Google successfully!', 'success')
        return redirect(url_for('uploads.gallery'))
    except Exception as e:
        flash('Google login failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

