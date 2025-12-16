from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from bhv.db import engine, Base, get_db
from bhv.models import User, Image
from bhv.auth import create_user, authenticate_user, require_user, logout_user
from bhv.storage import save_upload
from datetime import datetime

secret_key = os.environ.get('BHV_SECRET')
if not secret_key:
    raise ValueError(
        "BHV_SECRET environment variable is not set. "
        "This is required for session security. "
        "Set a strong, random secret key in your environment or .env file."
    )

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=secret_key)
templates = Jinja2Templates(directory='templates')
if os.path.isdir('frontend/dist'):
    app.mount('/', StaticFiles(directory='frontend/dist', html=True), name='frontend')
else:
    app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount('/images', StaticFiles(directory='data/images'), name='images')


@app.on_event('startup')
def startup():
    os.makedirs('data/images', exist_ok=True)
    Base.metadata.create_all(bind=engine)


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return RedirectResponse('/static/index.html')


@app.get('/api/images')
def api_images(db: Session = Depends(get_db)):
    imgs = db.query(Image).order_by(Image.created_at.desc()).limit(200).all()
    out = []
    for i in imgs:
        out.append({'id': i.id, 'filename': i.filename, 'narrative': i.narrative or '', 'url': f'/images/{i.filename}', 'thumb': f'/images/thumb-{i.filename}', 'created_at': i.created_at.isoformat()})
    return JSONResponse(out)


@app.get('/signup', response_class=HTMLResponse)
def signup_get(request: Request):
    return templates.TemplateResponse('signup.html', {'request': request})


@app.post('/signup')
def signup_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse('signup.html', {'request': request, 'error': 'Email exists'})
    user = create_user(db, email, password)
    request.session['user'] = {'id': user.id, 'email': user.email, 'role': user.role}
    return RedirectResponse('/', status_code=303)


@app.post('/api/signup')
async def api_signup(data: Request, db: Session = Depends(get_db)):
    payload = await data.json()
    email = payload.get('email')
    password = payload.get('password')
    if not email or not password:
        raise HTTPException(status_code=400)
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return JSONResponse({'error': 'exists'}, status_code=400)
    user = create_user(db, email, password)
    data.session['user'] = {'id': user.id, 'email': user.email, 'role': user.role}
    return JSONResponse({'id': user.id, 'email': user.email})


@app.get('/login', response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})


@app.post('/login')
def login_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse('login.html', {'request': request, 'error': 'Invalid'})
    request.session['user'] = {'id': user.id, 'email': user.email, 'role': user.role}
    return RedirectResponse('/', status_code=303)


@app.post('/api/login')
async def api_login(req: Request, db: Session = Depends(get_db)):
    p = await req.json()
    email = p.get('email')
    password = p.get('password')
    user = authenticate_user(db, email, password)
    if not user:
        return JSONResponse({'error': 'invalid'}, status_code=400)
    req.session['user'] = {'id': user.id, 'email': user.email, 'role': user.role}
    return JSONResponse({'id': user.id, 'email': user.email})


@app.get('/logout')
def logout(request: Request):
    logout_user(request)
    return RedirectResponse('/', status_code=303)


@app.post('/api/logout')
def api_logout(request: Request):
    logout_user(request)
    return JSONResponse({'ok': True})


@app.get('/upload', response_class=HTMLResponse)
def upload_get(request: Request, user=Depends(require_user)):
    return templates.TemplateResponse('upload.html', {'request': request, 'user': request.session.get('user')})


@app.post('/upload')
def upload_post(request: Request, file: UploadFile = File(...), narrative: str = Form(''), user=Depends(require_user), db: Session = Depends(get_db)):
    fname = save_upload(file)
    img = Image(user_id=user['id'], filename=fname, narrative=narrative, created_at=datetime.utcnow())
    db.add(img)
    db.commit()
    return RedirectResponse('/', status_code=303)


@app.post('/api/upload')
async def api_upload(file: UploadFile = File(...), narrative: str = Form(''), user: dict = Depends(require_user), db: Session = Depends(get_db)):
    fname = save_upload(file)
    img = Image(user_id=user['id'], filename=fname, narrative=narrative, created_at=datetime.utcnow())
    db.add(img)
    db.commit()
    return JSONResponse({'ok': True, 'filename': fname})


if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=8000, reload=False)
