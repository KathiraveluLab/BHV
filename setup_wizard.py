#!/usr/bin/env python3
"""
Quick Start Guide for BHV with Optimizations

This script helps you quickly set up BHV with all the new optimizations.
"""

import os
import secrets
import sys

def print_section(title):
    """Print a formatted section title."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def generate_secret():
    """Generate a secure secret key."""
    return secrets.token_urlsafe(32)

def main():
    """Run setup wizard."""
    print_section("BHV Setup Wizard - with Optimizations")
    
    print("This wizard will help you set up BHV with:")
    print("  ✅ Database optimization with indexes")
    print("  ✅ Caching layer (Redis/Memory)")
    print("  ✅ Input validation and security")
    print("  ✅ Rate limiting")
    print("  ✅ Pagination and performance")
    print("  ✅ Comprehensive logging")
    
    # Generate secret
    print_section("Step 1: Security Configuration")
    secret = generate_secret()
    print(f"Generated BHV_SECRET: {secret}")
    print("\nSave this key! You'll need it to run the application.")
    
    # Create .env file
    print_section("Step 2: Environment Configuration")
    create_env = input("Create .env file from .env.example? (y/n): ").lower() == 'y'
    
    if create_env:
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as f:
                env_content = f.read()
            
            # Replace secret placeholder
            env_content = env_content.replace(
                'your-secure-random-secret-key-here-minimum-32-characters',
                secret
            )
            
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ Created .env file with your secret key")
        else:
            print("❌ .env.example not found")
    
    # Setup instructions
    print_section("Step 3: Installation")
    print("To complete setup, run these commands:\n")
    
    commands = [
        "# Create virtual environment",
        "python -m venv .venv",
        "",
        "# Activate (Windows PowerShell)",
        ".\\venv\\Scripts\\Activate",
        "# Or on Linux/Mac:",
        "source .venv/bin/activate",
        "",
        "# Install dependencies",
        "pip install -r requirements.txt",
    ]
    
    if create_env:
        print("# .env file already created with secret key")
    else:
        commands.insert(0, f"# Set environment variable (or add to .env file)")
        commands.insert(1, f"export BHV_SECRET={secret}")
        commands.insert(2, "")
    
    for cmd in commands:
        print(cmd)
    
    # Run instructions
    print_section("Step 4: Running BHV")
    print("Once installed, start the application:\n")
    print("python app.py")
    print("\nAccess at: http://127.0.0.1:8000")
    
    # Features
    print_section("New Features Enabled")
    print("Database Optimization:")
    print("  • Composite indexes for faster queries")
    print("  • Connection pooling with health checks")
    print("  • Soft deletes for audit trails\n")
    
    print("Performance:")
    print("  • Image pagination (20 items/page by default)")
    print("  • Redis caching (or in-memory fallback)")
    print("  • Automatic image optimization\n")
    
    print("Security:")
    print("  • Strong password validation")
    print("  • Email validation")
    print("  • Rate limiting (30 req/60 sec)")
    print("  • File upload restrictions")
    print("  • UUID-based filenames\n")
    
    print("Monitoring:")
    print("  • Request/response logging")
    print("  • Error tracking")
    print("  • Health check endpoint (/health)")
    print("  • Metrics collection\n")
    
    # Configuration
    print_section("Configuration Options")
    print("Key environment variables you can configure:\n")
    print("DATABASE_URL")
    print("  • Default: sqlite:///./bhv.db")
    print("  • PostgreSQL: postgresql://user:pass@host/dbname\n")
    
    print("REDIS_URL")
    print("  • Default: (uses in-memory cache)")
    print("  • Example: redis://localhost:6379/0\n")
    
    print("RATE_LIMIT_REQUESTS")
    print("  • Default: 30 requests per window\n")
    
    print("MAX_FILE_SIZE")
    print("  • Default: 52428800 (50MB)\n")
    
    print("For all options, see .env.example\n")
    
    # Documentation
    print_section("Documentation")
    print("📄 README.md - Overview and basic setup")
    print("📄 OPTIMIZATIONS.md - Detailed optimization guide")
    print("📄 .env.example - All configurable options\n")
    
    print_section("Support")
    print("For issues or questions:")
    print("  • Check OPTIMIZATIONS.md for detailed feature docs")
    print("  • Review logs in console output")
    print("  • Check /health endpoint for system status\n")
    
    print("✅ Setup complete! Ready to run BHV with optimizations.\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
