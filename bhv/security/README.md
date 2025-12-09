# BHV Security Module

Authentication, authorization, and input validation for BHV.

## Password Management
```python
from bhv.security import PasswordManager

# Hash password
hashed = PasswordManager.hash_password("SecurePass123!")

# Verify password
valid = PasswordManager.verify_password("SecurePass123!", hashed)

# Validate strength
valid, error = PasswordManager.validate_password_strength("weak")
if not valid:
    print(error)
```

## Input Validation
```python
from bhv.security import Validator

# Validate email
if Validator.validate_email("user@example.com"):
    print("Valid email")

# Sanitize narrative (XSS prevention)
clean = Validator.sanitize_narrative("<script>alert('xss')</script>Hello")

# Validate image upload
valid, error = Validator.validate_image_upload(file)
if not valid:
    return error, 400
```

## Authentication
```python
from bhv.security import AuthManager, login_required, admin_required
from flask import Flask

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Protected route
@app.route('/dashboard')
@login_required
def dashboard():
    return "Welcome to dashboard"

# Admin route
@app.route('/admin')
@admin_required
def admin_panel():
    return "Admin Panel"

# Logout
@app.route('/logout')
def logout():
    AuthManager.logout_user()
    return redirect('/')
```

## Security Features

- **Password Security**: Bcrypt hashing (cost factor 12)
- **Session Management**: 24-hour timeout, IP tracking
- **Input Validation**: Email, username, file uploads
- **XSS Prevention**: HTML sanitization
- **CSRF Protection**: Token generation

## Testing
```bash
pytest tests/test_security.py -v
```

## HIPAA Compliance

- Secure password storage (bcrypt)
- Session tracking with IP addresses
- Input validation prevents data corruption
- Audit trail support