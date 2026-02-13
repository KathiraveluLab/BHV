"""
Simple tests for upload logic
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_app_creation():
    """Test that app can be created"""
    from bhv.app import create_app
    
    app = create_app()
    assert app is not None
    assert app.config['UPLOAD_FOLDER'] is not None

def test_routes_exist():
    """Test that main routes exist"""
    from bhv.app import create_app
    
    app = create_app()
    client = app.test_client()
    
    # Test routes return something
    response = client.get('/')
    assert response.status_code == 200
    
    response = client.get('/upload')
    assert response.status_code == 200
    
    response = client.get('/gallery')
    assert response.status_code == 200
    
    response = client.get('/health')
    assert response.status_code == 200

def test_health_endpoint():
    """Test health check endpoint"""
    from bhv.app import create_app
    
    app = create_app()
    client = app.test_client()
    
    response = client.get('/health')
    data = response.get_json()
    
    assert data['status'] == 'ok'
    assert data['service'] == 'BHV'