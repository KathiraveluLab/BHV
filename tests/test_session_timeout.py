"""Tests for session timeout functionality"""
import time
import pytest


def test_session_timeout_configuration(client):
    """Test that session timeout is configured correctly"""
    from datetime import timedelta
    timeout = client.application.config.get('PERMANENT_SESSION_LIFETIME')
    assert timeout == timedelta(minutes=15)


def test_ping_endpoint_requires_login(client):
    """Test that ping endpoint requires authentication"""
    response = client.get('/ping')
    # Should redirect to login (302) or return 401
    assert response.status_code in [302, 401]


def test_ping_endpoint_works_when_logged_in(client, auth):
    """Test that ping endpoint returns success when authenticated"""
    # Login first
    auth.login()
    
    # Then test ping
    response = client.get('/ping')
    assert response.status_code == 200
    assert b'status' in response.data
    assert b'ok' in response.data


def test_secure_cookie_configuration(client):
    """Test that session cookies have security flags enabled"""
    app = client.application
    assert app.config.get('SESSION_COOKIE_HTTPONLY') is True
    assert app.config.get('SESSION_COOKIE_SECURE') is True
    assert app.config.get('SESSION_COOKIE_SAMESITE') == 'Lax'


def test_session_permanent_lifetime(client):
    """Test session lifetime is 15 minutes"""
    from datetime import timedelta
    lifetime = client.application.config.get('PERMANENT_SESSION_LIFETIME')
    assert lifetime.total_seconds() == 900  # 15 minutes