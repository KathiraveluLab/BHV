from bhv.app import app, db, User

print("=== Starting database initialization ===")

with app.app_context():
    print("Creating all database tables...")
    db.create_all()
    print("Tables created successfully!")
    
    print("Creating admin accounts...")
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
            print(f"✓ Admin exists: {username}")
    
    db.session.commit()
    print("=== Database initialization COMPLETE ===")