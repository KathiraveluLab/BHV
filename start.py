#!/usr/bin/env python3
"""
BHV Startup Script

This script provides an easy way to start the BHV application with
proper environment setup, dependency checking, and configuration validation.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_banner():
    """Print BHV startup banner."""
    print("=" * 60)
    print("🏥 BHV: Behavioral Health Vault")
    print("   Healthcare Image & Narrative Storage System")
    print("=" * 60)


def check_python_version():
    """Check if Python version meets requirements."""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"❌ Python {required_version[0]}.{required_version[1]}+ required")
        print(f"   Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    print(f"✅ Python {current_version[0]}.{current_version[1]} - OK")
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'flask',
        'werkzeug', 
        'psutil',
        'bcrypt',
        'cryptography'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    
    return True


def setup_environment():
    """Set up environment variables and directories."""
    print("\n🔧 Setting up environment...")
    
    # Create required directories
    directories = [
        'data',
        'media/uploads', 
        'logs',
        'static',
        'templates'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory: {directory}")
    
    # Set default environment variables if not set
    env_defaults = {
        'SECRET_KEY': 'dev-secret-key-change-in-production',
        'DATABASE_PATH': 'data/bhv.db',
        'UPLOAD_FOLDER': 'media/uploads',
        'HOST': '127.0.0.1',
        'PORT': '5000',
        'DEBUG': 'True'
    }
    
    for key, default_value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = default_value
            print(f"✅ Environment: {key} = {default_value}")
    
    return True


def run_basic_tests():
    """Run basic functionality tests."""
    print("\n🧪 Running basic tests...")
    
    try:
        # Import and run tests
        from tests.test_basic import run_basic_tests
        success = run_basic_tests()
        return success
    except ImportError:
        print("⚠️  Test module not found, skipping tests")
        return True
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


def start_application():
    """Start the BHV application."""
    print("\n🚀 Starting BHV application...")
    
    try:
        # Import and create app
        from app import create_app
        from config.settings import Config
        
        app = create_app()
        config = Config()
        server_config = config.get_server_config()
        
        print(f"🌐 Server: http://{server_config['host']}:{server_config['port']}")
        print(f"🔧 Debug Mode: {server_config['debug']}")
        print(f"📁 Upload Directory: {app.config['UPLOAD_FOLDER']}")
        print("\n💡 Default admin credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   ⚠️  CHANGE THESE IMMEDIATELY!")
        print("\n🛑 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Start the server
        app.run(
            host=server_config['host'],
            port=server_config['port'],
            debug=server_config['debug']
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 BHV application stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start application: {e}")
        return False
    
    return True


def main():
    """Main startup function."""
    print_banner()
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        print("\n💡 To install dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Run tests (optional)
    if '--skip-tests' not in sys.argv:
        if not run_basic_tests():
            print("\n⚠️  Some tests failed, but continuing...")
    
    # Start application
    if '--test-only' in sys.argv:
        print("\n✅ Test-only mode complete")
        sys.exit(0)
    
    start_application()


if __name__ == '__main__':
    main()