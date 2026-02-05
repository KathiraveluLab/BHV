from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse

from app.services.auth_service import (
    google_login_redirect,
    google_callback_handler
)
from db import get_db

router = APIRouter()

@router.get("/login/google")
async def login_google(request: Request):
    
    return await google_login_redirect(request)


@router.get("/auth/google")
async def google_callback(
    request: Request,
    db=Depends(get_db)
):
    return await google_callback_handler(request, db)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", 303)