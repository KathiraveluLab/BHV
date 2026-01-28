from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uvicorn
import os
import logging
from bhv.db import engine, Base, get_db
from bhv.models import User, Image
from bhv.auth import create_user, authenticate_user, require_user, logout_user
from bhv.storage import save_upload, delete_image
from bhv.cache import cache
from bhv.rate_limit import rate_limiter
from bhv.validation import validate_email, validate_password, validate_narrative, ValidationError
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

secret_key = os.environ.get('BHV_SECRET')
if not secret_key:
    raise ValueError(
        "BHV_SECRET environment variable is not set. "
        "This is required for session security. "
        "Set a strong, random secret key in your environment or .env file."
    )

app = FastAPI(title="BHV", description="Image sharing and narrative platform")

# Add middleware
app.add_middleware(SessionMiddleware, secret_key=secret_key, max_age=86400)
app.add_middleware(GZIPMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory='templates')
if os.path.isdir('frontend/dist'):
    app.mount('/', StaticFiles(directory='frontend/dist', html=True), name='frontend')
else:
    app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount('/images', StaticFiles(directory='data/images'), name='images')


@app.on_event('startup')
def startup():
    """Initialize database and directories."""
    os.makedirs('data/images', exist_ok=True)
    Base.metadata.create_all(bind=engine)
    logger.info("Application startup complete")


@app.on_event('shutdown')
def shutdown():
    """Cleanup on shutdown."""
    logger.info("Application shutdown")


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    """Redirect to static index."""
    return RedirectResponse('/static/index.html')


@app.get('/api/images')
def api_images(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get paginated images with caching."""
    cache_key = f"images:page:{page}:limit:{limit}"
    cached = cache.get(cache_key)
    if cached:
        return JSONResponse(cached)
    
    skip = (page - 1) * limit
    imgs = db.query(Image).filter(
        Image.is_deleted == False
    ).order_by(desc(Image.created_at)).offset(skip).limit(limit + 1).all()
    
    has_more = len(imgs) > limit
    imgs = imgs[:limit]
    
    out = []
    for i in imgs:
        out.append({
            'id': i.id,
            'filename': i.filename,
            'narrative': i.narrative or '',
            'url': f'/images/{i.filename}',
            'thumb': f'/images/thumb-{i.filename}',
            'created_at': i.created_at.isoformat()
        })
    
    result = {'images': out, 'has_more': has_more, 'page': page}
    cache.set(cache_key, result, ttl=300)  # Cache for 5 minutes
    
    return JSONResponse(result)


@app.get('/signup', response_class=HTMLResponse)
def signup_get(request: Request):
    """Serve signup form."""
    return templates.TemplateResponse('signup.html', {'request': request})


@app.post('/signup')
def signup_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Handle signup with validation."""
    try:
        # Validate input
        if not validate_email(email):
            return templates.TemplateResponse('signup.html', {'request': request, 'error': 'Invalid email format'})
        
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return templates.TemplateResponse('signup.html', {'request': request, 'error': error_msg})
        
        # Check existing user
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return templates.TemplateResponse('signup.html', {'request': request, 'error': 'Email already registered'})
        
        # Create user
        user = create_user(db, email, password)
        request.session['user'] = {'id': user.id, 'email': user.email, 'role': user.role}
        logger.info(f"New user signup: {email}")
        return RedirectResponse('/', status_code=303)
    except ValueError as e:
        return templates.TemplateResponse('signup.html', {'request': request, 'error': str(e)})
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return templates.TemplateResponse('signup.html', {'request': request, 'error': 'An error occurred'})


@app.post('/api/signup')
async def api_signup(data: Request, db: Session = Depends(get_db)):
    """API endpoint for signup."""
    try:
        payload = await data.json()
        email = payload.get('email', '').strip()
        password = payload.get('password', '')
        
        if not email or not password:
            raise HTTPException(status_code=400, detail='Email and password required')
        
        if not validate_email(email):
            return JSONResponse({'error': 'Invalid email format'}, status_code=400)
        
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return JSONResponse({'error': error_msg}, status_code=400)
        
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return JSONResponse({'error': 'Email already registered'}, status_code=400)
        
        user = create_user(db, email, password)
        data.session['user'] = {'id': user.id, 'email': user.email, 'role': user.role}
        return JSONResponse({'id': user.id, 'email': user.email})
    except Exception as e:
        logger.error(f"API signup error: {e}")
        raise HTTPException(status_code=500, detail='Signup failed')


@app.get('/login', response_class=HTMLResponse)
def login_get(request: Request):
    """Serve login form."""
    return templates.TemplateResponse('login.html', {'request': request})


@app.post('/login')
def login_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Handle login with validation."""
    try:
        email = email.strip().lower()
        user = authenticate_user(db, email, password)
        if not user:
            return templates.TemplateResponse('login.html', {'request': request, 'error': 'Invalid credentials'})
        
        request.session['user'] = {'id': user.id, 'email': user.email, 'role': user.role}
        logger.info(f"User login: {email}")
        return RedirectResponse('/', status_code=303)
    except Exception as e:
        logger.error(f"Login error: {e}")
        return templates.TemplateResponse('login.html', {'request': request, 'error': 'An error occurred'})


@app.post('/api/login')
async def api_login(req: Request, db: Session = Depends(get_db)):
    """API endpoint for login."""
    try:
        p = await req.json()
        email = p.get('email', '').strip().lower()
        password = p.get('password', '')
        
        user = authenticate_user(db, email, password)
        if not user:
            return JSONResponse({'error': 'Invalid credentials'}, status_code=401)
        
        req.session['user'] = {'id': user.id, 'email': user.email, 'role': user.role}
        return JSONResponse({'id': user.id, 'email': user.email})
    except Exception as e:
        logger.error(f"API login error: {e}")
        raise HTTPException(status_code=500, detail='Login failed')


@app.get('/logout')
def logout(request: Request):
    """Handle logout."""
    logout_user(request)
    return RedirectResponse('/', status_code=303)


@app.post('/api/logout')
def api_logout(request: Request):
    """API endpoint for logout."""
    logout_user(request)
    return JSONResponse({'ok': True})


@app.get('/upload', response_class=HTMLResponse)
def upload_get(request: Request, user=Depends(require_user)):
    """Serve upload form."""
    return templates.TemplateResponse('upload.html', {'request': request, 'user': request.session.get('user')})


@app.post('/upload')
def upload_post(
    request: Request,
    file: UploadFile = File(...),
    narrative: str = Form(''),
    user=Depends(require_user),
    db: Session = Depends(get_db)
):
    """Handle file upload with validation."""
    try:
        # Validate narrative
        if not validate_narrative(narrative):
            return templates.TemplateResponse('upload.html', {'request': request, 'error': 'Narrative too long'})
        
        # Save file
        fname = save_upload(file)
        
        # Clear cache
        cache.clear_pattern('images:*')
        
        # Save to database
        img = Image(
            user_id=user['id'],
            filename=fname,
            narrative=narrative.strip() or None,
            created_at=datetime.utcnow(),
            is_deleted=False
        )
        db.add(img)
        db.commit()
        
        logger.info(f"Image uploaded by user {user['id']}: {fname}")
        return RedirectResponse('/', status_code=303)
    except ValueError as e:
        logger.warning(f"Upload validation error: {e}")
        return templates.TemplateResponse('upload.html', {'request': request, 'error': str(e)})
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return templates.TemplateResponse('upload.html', {'request': request, 'error': 'Upload failed'})


@app.post('/api/upload')
async def api_upload(
    file: UploadFile = File(...),
    narrative: str = Form(''),
    user: dict = Depends(require_user),
    db: Session = Depends(get_db)
):
    """API endpoint for file upload."""
    try:
        if not validate_narrative(narrative):
            raise HTTPException(status_code=400, detail='Narrative too long')
        
        fname = save_upload(file)
        cache.clear_pattern('images:*')
        
        img = Image(
            user_id=user['id'],
            filename=fname,
            narrative=narrative.strip() or None,
            created_at=datetime.utcnow(),
            is_deleted=False
        )
        db.add(img)
        db.commit()
        
        logger.info(f"API upload by user {user['id']}: {fname}")
        return JSONResponse({'ok': True, 'filename': fname})
    except ValueError as e:
        logger.warning(f"API upload validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API upload error: {e}")
        raise HTTPException(status_code=500, detail='Upload failed')


@app.delete('/api/images/{image_id}')
def delete_image_endpoint(image_id: int, user=Depends(require_user), db: Session = Depends(get_db)):
    """Delete image (soft delete)."""
    try:
        img = db.query(Image).filter(Image.id == image_id).first()
        if not img:
            raise HTTPException(status_code=404, detail='Image not found')
        
        if img.user_id != user['id']:
            raise HTTPException(status_code=403, detail='Unauthorized')
        
        img.is_deleted = True
        db.commit()
        
        cache.clear_pattern('images:*')
        logger.info(f"Image deleted by user {user['id']}: {image_id}")
        return JSONResponse({'ok': True})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete image error: {e}")
        raise HTTPException(status_code=500, detail='Delete failed')


@app.get('/health')
def health_check():
    """Health check endpoint."""
    return JSONResponse({'status': 'healthy'})


if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=8000, reload=False)
