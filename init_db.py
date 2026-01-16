from bhv.app import app, db, User

print("=" * 50)
print("Starting BHV Database Initialization")
print("=" * 50)

with app.app_context():
    print("\n[1/3] Creating database tables...")
    db.create_all()
    print("✓ Database tables created successfully!")
    
    print("\n[2/3] Creating admin accounts...")
    admins = [
        ('yadavchiragg', 'yadav@bhv.com', 'Demo2024!'),
        ('pradeeban', 'pradeeban@bhv.com', 'BHV2024!'),
        ('mdxabu', 'mdxabu@bhv.com', 'BHV2024!')
    ]
    
    created_count = 0
    existing_count = 0
    
    for username, email, password in admins:
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            admin = User(username=username, email=email, is_admin=True)
            admin.set_password(password)
            db.session.add(admin)
            print(f"  ✓ Created admin: {username}")
            created_count += 1
        else:
            print(f"  - Admin already exists: {username}")
            existing_count += 1
    
    print("\n[3/3] Committing changes to database...")
    db.session.commit()
    print("✓ Database commit successful!")
    
    print("\n" + "=" * 50)
    print("Database Initialization Complete!")
    print(f"  - Admin accounts created: {created_count}")
    print(f"  - Admin accounts existing: {existing_count}")
    print(f"  - Total admin accounts: {created_count + existing_count}")
    print("=" * 50)
    print("\nYou can now login with:")
    print("  Username: yadavchiragg")
    print("  Password: Demo2024!")
    print("=" * 50)