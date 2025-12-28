"""
Simple tests for models (without database)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports_work():
    """Test that we can import models"""
    from bhv.app import User, Image, db
    assert User is not None
    assert Image is not None
    assert db is not None

def test_user_password_hashing():
    """Test password hashing works"""
    from bhv.app import User
    
    user = User(username='test', email='test@test.com')
    user.set_password('mypassword')
    
    # Password should be hashed
    assert user.password_hash != 'mypassword'
    assert len(user.password_hash) > 20

def test_user_password_check():
    """Test password verification"""
    from bhv.app import User
    
    user = User(username='test', email='test@test.com')
    user.set_password('correct')
    
    assert user.check_password('correct') == True
    assert user.check_password('wrong') == False