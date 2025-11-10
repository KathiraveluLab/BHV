"""Seed database with initial data."""
from app import create_app
from app.extensions import db
from app.models import User
from datetime import datetime


def seed_database():
    """
    Seed the database with initial test users.
    Note: Admin users should be configured via ADMIN_EMAILS in .env file.
    This script creates test users for development only.
    """
    app = create_app()
    
    with app.app_context():
        from app.config import Config
        
        # Create test user if it doesn't exist
        test_email = 'user@example.com'
        test_user = User.find_by_email(test_email)
        
        if not test_user:
            test_user = User.create(
                email=test_email,
                password='user123',
                role='user'  # Explicitly set as user
            )
            test_user.verify()  # Auto-verify test user
            print(f"Created test user: {test_email} / user123")
        else:
            print(f"Test user already exists: {test_email}")
        
        # Check if admin emails are configured
        from app.config import get_admin_emails
        admin_emails = get_admin_emails()
        if admin_emails:
            print(f"\n✅ Admin emails configured in .env: {', '.join(admin_emails)}")
            print("💡 Any user with email in ADMIN_EMAILS will automatically have admin access.")
            print("💡 You can add emails to ADMIN_EMAILS and existing users will get admin access immediately.")
        else:
            print("\n⚠️  No admin emails configured in ADMIN_EMAILS environment variable.")
            print("💡 Add admin emails to .env file: ADMIN_EMAILS=admin1@example.com,admin2@example.com")
            print("💡 After adding emails, users will automatically get admin access (no script needed!)")
        
        print("\nDatabase seeded successfully!")
        print("\nTest user credentials:")
        print(f"User: {test_email} / user123")


if __name__ == '__main__':
    seed_database()

