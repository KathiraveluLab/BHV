from bhv.app import create_app, db, User

app = create_app()

with app.app_context():
    db.create_all()
    
    admins = [
        (os.environ.get('ADMIN_USER_1', 'yadavchiragg'), os.environ.get('ADMIN_EMAIL_1', 'yadav@bhv.com'), os.environ.get('ADMIN_PASS_1')),
        (os.environ.get('ADMIN_USER_2', 'pradeeban'), os.environ.get('ADMIN_EMAIL_2', 'pradeeban@bhv.com'), os.environ.get('ADMIN_PASS_2')),
        (os.environ.get('ADMIN_USER_3', 'mdxabu'), os.environ.get('ADMIN_EMAIL_3', 'mdxabu@bhv.com'), os.environ.get('ADMIN_PASS_3'))
    ]
    
    for username, email, password in admins:
        if not User.query.filter_by(username=username).first():
            user = User(username=username, email=email, is_admin=True)
            user.set_password(password)
            db.session.add(user)
            print(f'Created: {username}')
    
    db.session.commit()
    print('Done!')