"""Script to create admin users manually.
Admin email must be in ADMIN_EMAILS in .env file."""
from app import create_app
from app.models import User
from app.config import is_admin_email, get_admin_emails

def create_admin_user(email, password):
    """Create an admin user manually."""
    app = create_app()
    
    with app.app_context():
        # Check if email matches admin email
        if not is_admin_email(email):
            print(f"❌ Error: {email} is not in ADMIN_EMAILS in .env file.")
            from app.config import get_admin_emails
            admin_emails = get_admin_emails()
            print(f"Current admin emails: {', '.join(admin_emails) if admin_emails else 'None'}")
            print("\nTo add admin email, add it to .env file:")
            print(f"ADMIN_EMAILS={email}")
            if admin_emails:
                print(f"Or append to existing: ADMIN_EMAILS={','.join(admin_emails)},{email}")
            return False
        
        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            # Check if they're admin (using dynamic check)
            if existing_user.is_admin():
                print(f"✅ User {email} has admin access (email is in ADMIN_EMAILS)")
                print(f"✅ Note: Admin access is granted via ADMIN_EMAILS in .env, no database update needed")
                if not existing_user.is_verified:
                    existing_user.verify()
                    print(f"✅ Verified user: {email}")
                return True
            else:
                # User exists but email not in ADMIN_EMAILS
                print(f"⚠️  User {email} exists but email is not in ADMIN_EMAILS.")
                print(f"💡 To grant admin access, add email to ADMIN_EMAILS in .env file.")
                admin_emails = get_admin_emails()
                if admin_emails:
                    print(f"💡 Example: ADMIN_EMAILS={','.join(admin_emails)},{email}")
                else:
                    print(f"💡 Example: ADMIN_EMAILS={email}")
                print(f"💡 No need to run this script - just set in .env and the user will get admin access automatically!")
                return False
        
        # Create admin user
        admin = User.create(
            email=email,
            password=password,
            role='admin'  # Explicitly set as admin
        )
        admin.verify()  # Auto-verify admin
        
        print(f"✅ Admin user created successfully: {email}")
        print(f"✅ Password set and account verified")
        return True

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python create_admin.py <email> <password>")
        print("\nExample:")
        print("  python create_admin.py admin@example.com admin123")
        print("\nNote: Email must be in ADMIN_EMAILS in .env file")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    create_admin_user(email, password)

