from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.database import users_collection
from app.routes import admin, auth, gallery, upload
from app.services.auth_service import get_current_user_from_request


app = FastAPI(title="Behavioral Health Vault")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
app.mount("/storage", StaticFiles(directory=str(BASE_DIR / "storage")), name="storage")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(gallery.router, prefix="/gallery", tags=["gallery"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.on_event("startup")
def setup_indexes() -> None:
    users_collection.create_index("email", unique=True)


@app.get("/")
def index(request: Request):
    user = get_current_user_from_request(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return RedirectResponse(url="/auth/login", status_code=303)


@app.get("/dashboard")
def dashboard(request: Request):
    user = get_current_user_from_request(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})
