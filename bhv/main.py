from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import shutil
from pathlib import Path
import uvicorn

app = FastAPI()

APP_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = APP_DIR / "static"
TEMPLATE_DIR = APP_DIR / "ui"
UPLOAD_DIR = STATIC_DIR / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)
# Auth

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/")
def login():
    return RedirectResponse("/dashboard", status_code=302)

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    fake_images = []
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "images": fake_images
    })

# Upload images

@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload")
def upload_image(
    image: UploadFile = File(...),
    title: str = Form(""),
    description: str = Form(""),
    emotion: str = Form("")
):
    path = UPLOAD_DIR / f"{uuid.uuid4().hex}{Path(image.filename).suffix}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return RedirectResponse("/dashboard", status_code=302)

# Admin
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    all_images = []
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "images": all_images
    })

def run():
    uvicorn.run("bhv.main:app", host="0.0.0.0", port=8000, reload=False)
