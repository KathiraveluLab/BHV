"""
Basic tests for BHV application functionality.

This module provides simple tests to verify core application components
are working correctly after installation.
"""

import unittest
import tempfile
import os
from pathlib import Path

# Import application components
try:
    from app import create_app
    from config.settings import Config
    from models.database import init_db, get_db_connection
    from utils.file_handler import FileHandler
    from utils.auth import AuthManager
    from utils.diagnostics import DiagnosticsManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")


class TestBHVBasics(unittest.TestCase):
    """Basic functionality tests for BHV application."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        os.environ['DATABASE_PATH'] = os.path.join(self.test_dir, 'test.db')
        os.environ['UPLOAD_FOLDER'] = os.path.join(self.test_dir, 'uploads')
        os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_config_loading(self):
        """Test configuration loading."""
        config = Config()
        self.assertIsNotNone(config.SECRET_KEY)
        self.assertTrue(len(config.SECRET_KEY) > 0)
    
    def test_database_initialization(self):
        """Test database initialization."""
        try:
            init_db()
            conn = get_db_connection()
            
            # Test basic query
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [row[0] for row in result]
            
            expected_tables = ['users', 'images', 'narratives', 'audit_log', 'user_sessions']
            for table in expected_tables:
                self.assertIn(table, table_names)
            
            conn.close()
        except Exception as e:
            self.fail(f"Database initialization failed: {e}")
    
    def test_file_handler_creation(self):
        """Test file handler initialization."""
        upload_folder = os.path.join(self.test_dir, 'uploads')
        file_handler = FileHandler(upload_folder)
        
        self.assertTrue(Path(upload_folder).exists())
        self.assertEqual(str(file_handler.upload_folder), upload_folder)
    
    def test_auth_manager_creation(self):
        """Test authentication manager initialization."""
        auth_manager = AuthManager()
        self.assertIsNotNone(auth_manager)
        
        # Test password hashing
        password = "test_password_123!"
        hash_result, salt = auth_manager.hash_password(password)
        self.assertIsNotNone(hash_result)
        self.assertIsNotNone(salt)
        
        # Test password verification
        is_valid = auth_manager.verify_password(password, hash_result, salt)
        self.assertTrue(is_valid)
    
    def test_diagnostics_manager_creation(self):
        """Test diagnostics manager initialization."""
        diagnostics = DiagnosticsManager()
        self.assertIsNotNone(diagnostics)
        
        # Test basic system info retrieval
        system_info = diagnostics.get_system_info()
        self.assertIsInstance(system_info, dict)
    
    def test_flask_app_creation(self):
        """Test Flask application creation."""
        try:
            app = create_app()
            self.assertIsNotNone(app)
            
            # Test app configuration
            self.assertIn('SECRET_KEY', app.config)
            self.assertIn('UPLOAD_FOLDER', app.config)
            
            # Test basic route
            with app.test_client() as client:
                response = client.get('/')
                self.assertEqual(response.status_code, 200)
                
        except Exception as e:
            self.fail(f"Flask app creation failed: {e}")


class TestBHVSecurity(unittest.TestCase):
    """Security-related tests for BHV application."""
    
    def test_password_strength_validation(self):
        """Test password strength validation."""
        auth_manager = AuthManager()
        
        # Test weak passwords
        weak_passwords = [
            "123456",
            "password",
            "abc",
            "PASSWORD123",  # No special chars
            "password!"     # No uppercase or numbers
        ]
        
        for password in weak_passwords:
            is_valid, message = auth_manager.validate_password_strength(password)
            self.assertFalse(is_valid, f"Password '{password}' should be invalid")
        
        # Test strong password
        strong_password = "StrongP@ssw0rd123!"
        is_valid, message = auth_manager.validate_password_strength(strong_password)
        self.assertTrue(is_valid, f"Strong password should be valid: {message}")
    
    def test_file_validation(self):
        """Test file upload validation."""
        upload_folder = tempfile.mkdtemp()
        file_handler = FileHandler(upload_folder)
        
        # Test allowed extensions
        allowed_files = [
            "image.jpg", "photo.png", "scan.jpeg", 
            "drawing.gif", "picture.bmp", "document.tiff"
        ]
        
        for filename in allowed_files:
            self.assertTrue(file_handler.allowed_file(filename))
        
        # Test disallowed extensions
        disallowed_files = [
            "script.js", "document.pdf", "archive.zip", 
            "executable.exe", "config.txt"
        ]
        
        for filename in disallowed_files:
            self.assertFalse(file_handler.allowed_file(filename))


def run_basic_tests():
    """Run basic functionality tests."""
    print("🧪 Running BHV Basic Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestBHVBasics))
    suite.addTest(unittest.makeSuite(TestBHVSecurity))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed! BHV is ready to use.")
    else:
        print("❌ Some tests failed. Please check the output above.")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_basic_tests()
    exit(0 if success else 1)