import os
import sys

def init_database():
    """Initialize database with proper error handling"""
    try:
        print("=== Starting database initialization ===")
        
        # Fix DATABASE_URL for SQLAlchemy 1.4+ (postgres:// -> postgresql://)
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            os.environ['DATABASE_URL'] = database_url.replace('postgres://', 'postgresql://', 1)
            print(f"✓ Fixed DATABASE_URL: postgres:// -> postgresql://")
        
        from bhv.app import app, db, User
        
        with app.app_context():
            print("Creating all database tables...")
            db.create_all()
            print("✓ Tables created successfully!")
            
            # Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✓ Tables in database: {tables}")
            
            if 'user' not in tables:
                raise Exception("ERROR: User table was not created!")
            
            print("\nCreating admin accounts...")
            admins = [
                ('yadavchiragg', 'yadav@bhv.com', 'Demo2024!'),
                ('pradeeban', 'pradeeban@bhv.com', 'BHV2024!'),
                ('mdxabu', 'mdxabu@bhv.com', 'BHV2024!')
            ]
            
            for username, email, password in admins:
                existing = User.query.filter_by(username=username).first()
                if not existing:
                    admin = User(username=username, email=email, is_admin=True)
                    admin.set_password(password)
                    db.session.add(admin)
                    print(f"✓ Created admin: {username}")
                else:
                    print(f"✓ Admin already exists: {username}")
            
            db.session.commit()
            print("\n=== Database initialization COMPLETE ===")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR during database initialization:", file=sys.stderr)
        print(f"❌ {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    init_database()