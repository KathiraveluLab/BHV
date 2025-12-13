"""Tests for authentication routes."""
import pytest
from app import app
from bhv.database import db
from bhv.models import User


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_index_page(client):
    """Test index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Behavioral Health Vault' in response.data


def test_register_page_get(client):
    """Test registration page loads."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Create Account' in response.data


def test_register_success(client):
    """Test successful user registration."""
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful' in response.data


def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    # Register first user
    client.post('/register', data={
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    })
    
    # Try to register again with same email
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'NewPass123!',
        'confirm_password': 'NewPass123!'
    }, follow_redirects=True)
    
    assert b'Email already registered' in response.data


def test_register_password_mismatch(client):
    """Test registration with mismatched passwords."""
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'confirm_password': 'DifferentPass123!'
    }, follow_redirects=True)
    
    assert b'Passwords do not match' in response.data


def test_register_weak_password(client):
    """Test registration with weak password."""
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'weak',
        'confirm_password': 'weak'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Password must be at least 8 characters long" in response.data


def test_login_page_get(client):
    """Test login page loads."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data


def test_login_success(client):
    """Test successful login."""
    # Register user first
    client.post('/register', data={
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    })
    
    # Login
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'SecurePass123!'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Welcome back' in response.data


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'WrongPass123!'
    }, follow_redirects=True)
    
    assert b'Invalid email or password' in response.data


def test_dashboard_requires_login(client):
    """Test dashboard redirects when not logged in."""
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Please login' in response.data


def test_logout(client):
    """Test logout functionality."""
    # Register and login
    client.post('/register', data={
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    })
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'SecurePass123!'
    })
    
    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert b'logged out' in response.data