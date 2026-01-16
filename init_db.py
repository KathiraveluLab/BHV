from bhv.app import app, db, User

print("Starting database initialization...")

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    
    print("Creating admin accounts...")
    admins = [
        ('yadavchiragg', 'yadav@bhv.com', 'Demo2024!'),
        ('pradeeban', 'pradeeban@bhv.com', 'BHV2024!'),
        ('mdxabu', 'mdxabu@bhv.com', 'BHV2024!')
    ]
    
    for username, email, password in admins:
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            admin = User(username=username, email=email, is_admin=True)
            admin.set_password(password)
            db.session.add(admin)
            print(f"Created admin: {username}")
        else:
            print(f"Admin already exists: {username}")
    
    db.session.commit()
    print("Database initialization completed successfully!")