from datetime import timedelta
from flask import session, request, redirect, url_for, flash
import time

# Add to app configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# Session timeout check
@app.before_request
def check_session_timeout():
    """
    Implement automatic session timeout for HIPAA compliance.
    Sessions expire after 15 minutes of inactivity (§164.312(a)(2)(iii))
    """
    if current_user.is_authenticated:
        session.permanent = True
        
        # Check last activity
        last_activity = session.get('last_activity')
        if last_activity:
            # Calculate time since last activity
            elapsed = time.time() - last_activity
            
            # Timeout after 15 minutes (900 seconds)
            if elapsed > 900:
                logout_user()
                flash('Your session expired due to inactivity. Please log in again.', 'warning')
                return redirect(url_for('login'))
        
        # Update last activity timestamp
        session['last_activity'] = time.time()