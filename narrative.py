from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse
import sqlite3

from db import get_db

router = APIRouter()

@router.post("/update-narrative")
def update_narrative(
    request: Request,
    filename: str = Form(...),
    narrative: str = Form(""),
    db: sqlite3.Connection = Depends(get_db)
):
    if not request.session.get("user"):
        return RedirectResponse("/login", 303)

    cur = db.cursor()
    cur.execute(
        """
        UPDATE images
        SET narrative = ?
        WHERE filename = ? AND user_name = ?
        """,
        (narrative.strip(), filename, request.session["user"])
    )

    db.commit()
    return RedirectResponse("/gallery", 303)
