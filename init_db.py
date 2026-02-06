from bhv.app import app, db, User

with app.app_context():
    db.create_all()
    
    admins = [
        ('yadavchiragg', 'yadav@bhv.com', 'Demo2024!'),
        ('pradeeban', 'pradeeban@bhv.com', 'BHV2024!'),
        ('mdxabu', 'mdxabu@bhv.com', 'BHV2024!')
    ]
    
    for username, email, password in admins:
        if not User.query.filter_by(username=username).first():
            admin = User(username=username, email=email, is_admin=True)
            admin.set_password(password)
            db.session.add(admin)
    
    db.session.commit()
    print("Database initialized successfully!")