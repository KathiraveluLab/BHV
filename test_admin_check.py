"""Test script to verify admin email checking works correctly."""
from app import create_app
from app.models import User
from app.config import get_admin_emails, is_admin_email
import os

def test_admin_checking():
    """Test admin email checking functionality."""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Admin Email Checking Test")
        print("=" * 60)
        
        # Get admin emails from .env
        admin_emails = get_admin_emails()
        print(f"\n📋 Admin emails from ADMIN_EMAILS in .env:")
        if admin_emails:
            for email in admin_emails:
                print(f"   - {email}")
        else:
            print("   ⚠️  No admin emails found in ADMIN_EMAILS")
            print("\n💡 To add admin emails, add to .env file:")
            print("   ADMIN_EMAILS=admin1@example.com,admin2@example.com")
        
        # Test with environment variable directly
        env_admin_emails = os.environ.get('ADMIN_EMAILS', '')
        print(f"\n📋 ADMIN_EMAILS from os.environ: '{env_admin_emails}'")
        
        # Test a few emails
        test_emails = ['test@example.com']
        if admin_emails:
            test_emails.extend(admin_emails[:2])  # Test first 2 admin emails
        
        print(f"\n🧪 Testing email checks:")
        for email in test_emails:
            is_admin = is_admin_email(email)
            print(f"   {email}: {'✅ Admin' if is_admin else '❌ Not Admin'}")
        
        # Test with existing users
        print(f"\n👤 Checking existing users:")
        # Get some users from database
        from app.models import get_db
        users = list(get_db().users.find().limit(5))
        
        if users:
            for user_data in users:
                user = User(user_data)
                email = user.email
                stored_role = user.get_stored_role()
                dynamic_role = user.role
                is_admin_result = user.is_admin()
                
                print(f"\n   Email: {email}")
                print(f"      Stored role (DB): {stored_role}")
                print(f"      Dynamic role: {dynamic_role}")
                print(f"      is_admin(): {is_admin_result}")
                print(f"      In ADMIN_EMAILS: {is_admin_email(email)}")
        else:
            print("   No users found in database")
        
        print("\n" + "=" * 60)
        print("💡 Key Points:")
        print("   - Dynamic role checks ADMIN_EMAILS at runtime")
        print("   - If email is in ADMIN_EMAILS → always admin")
        print("   - Database role doesn't matter if email is in ADMIN_EMAILS")
        print("   - Add email to ADMIN_EMAILS in .env → user gets admin access immediately")
        print("=" * 60)

if __name__ == '__main__':
    test_admin_checking()

