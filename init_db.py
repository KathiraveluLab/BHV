from bhv.app import create_app, db, User

app = create_app()

with app.app_context():
    db.create_all()
    
    admins = [
        ('yadavchiragg', 'yadav@bhv.com', 'Demo2024!'),
        ('pradeeban', 'pradeeban@bhv.com', 'BHV2024!'),
        ('mdxabu', 'mdxabu@bhv.com', 'BHV2024!')
    ]
    
    for username, email, password in admins:
        if not User.query.filter_by(username=username).first():
            user = User(username=username, email=email, is_admin=True)
            user.set_password(password)
            db.session.add(user)
            print(f'Created: {username}')
    
    db.session.commit()
    print('Done!')