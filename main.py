from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext

import sqlite3
import os
import uuid
import shutil
import json
from pathlib import Path

from db import get_db, init_db
from narrative import router as narrative_router
from fuzzy_emotion import detect_fuzzy_emotion
from config import SECRET_KEY, GOOGLE_REDIRECT_URI
from auth_google import oauth


app = FastAPI()
init_db()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.include_router(narrative_router)

templates = Jinja2Templates(directory="templates")
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

UPLOAD_DIR = Path("static/uploads").resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/login/google")
async def login_google(request: Request):
    return await oauth.google.authorize_redirect(
        request,
        GOOGLE_REDIRECT_URI
    )


@app.get("/auth/google")
async def google_callback(
    request: Request,
    db: sqlite3.Connection = Depends(get_db)
):
    token = await oauth.google.authorize_access_token(request)
    user = token.get("userinfo")

    if not user:
        return RedirectResponse("/login", 303)

    email = user["email"]
    name = user.get("name") or email.split("@")[0]

    cur = db.cursor()
    cur.execute("SELECT name FROM users WHERE email=?", (email,))
    row = cur.fetchone()

    if not row:
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, "")
        )
        db.commit()

    request.session["user"] = name
    return RedirectResponse("/", 303)


@app.get("/")
def home(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", 303)

    return templates.TemplateResponse(
        "home.html",
        {"request": request, "user": request.session["user"]}
    )


@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
def signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: sqlite3.Connection = Depends(get_db)
):
    password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    hashed = pwd_ctx.hash(password)
    cur = db.cursor()

    try:
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Email already exists"}
        )

    return RedirectResponse("/login", 303)


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: sqlite3.Connection = Depends(get_db)
):
    cur = db.cursor()
    cur.execute("SELECT name, password FROM users WHERE email=?", (email,))
    row = cur.fetchone()

    password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")

    if row and pwd_ctx.verify(password, row["password"]):
        request.session["user"] = row["name"]
        return RedirectResponse("/", 303)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid credentials"}
    )


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", 303)


@app.get("/gallery")
def gallery(
    request: Request,
    db: sqlite3.Connection = Depends(get_db)
):
    if not request.session.get("user"):
        return RedirectResponse("/login", 303)

    cur = db.cursor()
    cur.execute("""
        SELECT filename, metadata, narrative
        FROM images
        WHERE user_name=?
    """, (request.session["user"],))

    rows = cur.fetchall()
    images = []

    for fn, metadata_json, narrative in rows:
        try:
            meta = json.loads(metadata_json) if metadata_json else {}
        except json.JSONDecodeError:
            meta = {}
        images.append((fn, meta, narrative))

    return templates.TemplateResponse(
        "gallery.html",
        {
            "request": request,
            "images": images,
            "profile_user": request.session["user"],
            "current_user": request.session["user"]
        }
    )


@app.post("/upload")
def upload_image(
    request: Request,
    image: UploadFile = File(...),
    visibility: str = Form("private"),
    db: sqlite3.Connection = Depends(get_db)
):
    if not request.session.get("user"):
        return RedirectResponse("/login", 303)

    ext = os.path.splitext(image.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    path = (UPLOAD_DIR / filename).resolve()

    with open(path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    metadata = detect_fuzzy_emotion(str(path))

    cur = db.cursor()
    cur.execute("""
        INSERT INTO images (user_name, filename, metadata, visibility)
        VALUES (?, ?, ?, ?)
    """, (
        request.session["user"],
        filename,
        json.dumps(metadata),
        visibility
    ))
    db.commit()

    return RedirectResponse("/gallery", 303)


@app.post("/delete/{filename}")
def delete_image(
    request: Request,
    filename: str,
    db: sqlite3.Connection = Depends(get_db)
):
    if not request.session.get("user"):
        return RedirectResponse("/login", 303)

    safe_name = Path(filename).name
    file_path = (UPLOAD_DIR / safe_name).resolve()

    if not str(file_path).startswith(str(UPLOAD_DIR)):
        raise HTTPException(status_code=400, detail="Invalid filename")

    cur = db.cursor()
    cur.execute(
        "DELETE FROM images WHERE filename=? AND user_name=?",
        (safe_name, request.session["user"])
    )
    db.commit()

    if file_path.exists():
        file_path.unlink()

    return RedirectResponse("/gallery", 303)
