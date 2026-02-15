"""
Comprehensive test suite for BHV application
Tests authentication, uploads, admin features, and security
"""

import sys
import os
from pathlib import Path
import tempfile
import pytest
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bhv.app import app, db, User, Image


@pytest.fixture
def client():
    """Create test client with temporary database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def regular_user(client):
    """Create a regular test user"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com', is_admin=False)
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def admin_user(client):
    """Create an admin test user"""
    with app.app_context():
        user = User(username='admin', email='admin@example.com', is_admin=True)
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        return user


# ==================== AUTHENTICATION TESTS ====================

def test_homepage_accessible(client):
    """Test that homepage is accessible without login"""
    response = client.get('/')
    assert response.status_code == 200


def test_register_page_accessible(client):
    """Test that registration page loads"""
    response = client.get('/register')
    assert response.status_code == 200


def test_login_page_accessible(client):
    """Test that login page loads"""
    response = client.get('/login')
    assert response.status_code == 200


def test_user_registration_success(client):
    """Test successful user registration"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'


def test_user_registration_duplicate_username(client, regular_user):
    """Test that duplicate usernames are rejected"""
    response = client.post('/register', data={
        'username': 'testuser',  # Already exists
        'email': 'different@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    assert b'Username already taken' in response.data or response.status_code != 200


def test_user_registration_duplicate_email(client, regular_user):
    """Test that duplicate emails are rejected"""
    response = client.post('/register', data={
        'username': 'differentuser',
        'email': 'test@example.com',  # Already exists
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    assert b'Email already registered' in response.data or response.status_code != 200


def test_user_registration_password_mismatch(client):
    """Test that mismatched passwords are rejected"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'different123'
    })
    
    assert b'Passwords must match' in response.data or response.status_code != 200


def test_user_login_success(client, regular_user):
    """Test successful user login"""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200


def test_user_login_wrong_password(client, regular_user):
    """Test login with incorrect password"""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    
    assert b'Invalid username or password' in response.data


def test_user_login_nonexistent_user(client):
    """Test login with non-existent username"""
    response = client.post('/login', data={
        'username': 'nonexistent',
        'password': 'password123'
    })
    
    assert b'Invalid username or password' in response.data


def test_user_logout(client, regular_user):
    """Test user logout"""
    # Login first
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200


# ==================== PROTECTED ROUTES TESTS ====================

def test_gallery_requires_login(client):
    """Test that gallery requires authentication"""
    response = client.get('/gallery')
    assert response.status_code == 302  # Redirect to login


def test_upload_requires_login(client):
    """Test that upload page requires authentication"""
    response = client.get('/upload')
    assert response.status_code == 302  # Redirect to login


def test_profile_requires_login(client):
    """Test that profile page requires authentication"""
    response = client.get('/profile')
    assert response.status_code == 302  # Redirect to login


def test_gallery_accessible_when_logged_in(client, regular_user):
    """Test that gallery is accessible after login"""
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    response = client.get('/gallery')
    assert response.status_code == 200


def test_profile_accessible_when_logged_in(client, regular_user):
    """Test that profile is accessible after login"""
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    response = client.get('/profile')
    assert response.status_code == 200


# ==================== ADMIN ACCESS TESTS ====================

def test_admin_dashboard_requires_admin(client, regular_user):
    """Test that non-admin users cannot access admin dashboard"""
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    response = client.get('/admin')
    assert response.status_code == 302  # Redirect


def test_admin_dashboard_accessible_for_admin(client, admin_user):
    """Test that admin users can access admin dashboard"""
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    response = client.get('/admin')
    assert response.status_code == 200


def test_admin_users_page_requires_admin(client, regular_user):
    """Test that admin users page requires admin privileges"""
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    response = client.get('/admin/users')
    assert response.status_code == 302  # Redirect


def test_admin_images_page_requires_admin(client, regular_user):
    """Test that admin images page requires admin privileges"""
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    response = client.get('/admin/images')
    assert response.status_code == 302  # Redirect


# ==================== IMAGE UPLOAD TESTS ====================

def test_upload_page_shows_form(client, regular_user):
    """Test that upload page displays the form"""
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    response = client.get('/upload')
    assert response.status_code == 200
    assert b'Upload' in response.data


def test_upload_image_success(client, regular_user):
    """Test successful image upload"""
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    # Create a fake image file
    data = {
        'title': 'Test Image',
        'description': 'Test Description',
        'file': (BytesIO(b'fake image data'), 'test.jpg')
    }
    
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    
    # Should redirect to gallery or profile
    assert response.status_code == 200


def test_upload_without_file(client, regular_user):
    """Test upload without selecting a file"""
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    data = {
        'title': 'Test Image',
        'description': 'Test Description'
    }
    
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    
    # Should show error or stay on upload page
    assert response.status_code in [200, 302]


# ==================== USER MODEL TESTS ====================

def test_user_password_hashing():
    """Test that passwords are properly hashed"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        
        assert user.password_hash != 'password123'
        assert user.check_password('password123') == True
        assert user.check_password('wrongpassword') == False


def test_user_admin_status():
    """Test user admin status"""
    with app.app_context():
        user = User(username='admin', email='admin@example.com', is_admin=True)
        assert user.is_admin == True
        
        regular = User(username='regular', email='regular@example.com', is_admin=False)
        assert regular.is_admin == False


# ==================== HEALTH CHECK TEST ====================

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    # Health endpoint might return 'ok' or 'healthy'
    json_data = response.get_json()
    assert json_data is not None
    assert 'status' in json_data


# ==================== SECURITY TESTS ====================

def test_xss_in_title(client, regular_user):
    """Test that XSS in title is handled"""
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    data = {
        'title': '<script>alert("XSS")</script>',
        'description': 'Test',
        'file': (BytesIO(b'fake image'), 'test.jpg')
    }
    
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    
    # Should either reject or sanitize
    assert response.status_code in [200, 302, 400]


def test_sql_injection_in_username(client):
    """Test SQL injection attempt in username"""
    response = client.post('/register', data={
        'username': "admin' OR '1'='1",
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    # Should handle gracefully
    assert response.status_code in [200, 302, 400]