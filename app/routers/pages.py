from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def home(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", 303)

    return templates.TemplateResponse(
        "home.html",
        {"request": request, "user": request.session["user"]}
    )

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})
