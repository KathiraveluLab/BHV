from fastapi import Request
from fastapi.responses import RedirectResponse

from auth_google import oauth
from config import GOOGLE_REDIRECT_URI

def _get_username(user: dict) -> str:
    return user.get("name") or user["email"].split("@")[0]


async def google_login_redirect(request: Request):
    return await oauth.google.authorize_redirect(
        request,
        GOOGLE_REDIRECT_URI
    )


async def google_callback_handler(request: Request, db):
    token = await oauth.google.authorize_access_token(request)
    user = token.get("userinfo")

    if not user:
        return RedirectResponse("/login", 303)

    email = user["email"]
    name = _get_username(user)

    cur = db.cursor()
    cur.execute("SELECT name FROM users WHERE email=?", (email,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, None)
        db.commit()

    request.session["user"] = name
    return RedirectResponse("/", 303)
