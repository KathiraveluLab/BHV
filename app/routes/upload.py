from datetime import datetime

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.database import images_collection
from app.services.auth_service import get_current_user_from_request
from app.services.image_service import is_allowed_image, is_valid_sentiment, save_image_file


router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
SENTIMENT_CHOICES = ["positive", "neutral", "negative"]


@router.get("/")
def upload_page(request: Request):
    user = get_current_user_from_request(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "user": user,
            "error": None,
            "sentiments": SENTIMENT_CHOICES,
        },
    )


@router.post("/")
def upload_image(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    sentiment: str = Form("neutral"),
    image: UploadFile = File(...),
):
    user = get_current_user_from_request(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    sentiment = sentiment.strip().lower()
    if not is_valid_sentiment(sentiment):
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "user": user,
                "error": "Please select a valid sentiment.",
                "sentiments": SENTIMENT_CHOICES,
            },
            status_code=400,
        )

    if not image.filename or not is_allowed_image(image.filename):
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "user": user,
                "error": "Please upload a valid file: jpg, jpeg, png, gif, webp, or pdf.",
                "sentiments": SENTIMENT_CHOICES,
            },
            status_code=400,
        )

    image_path = save_image_file(image, user["id"])
    images_collection.insert_one(
        {
            "user_id": user["id"],
            "title": title.strip(),
            "description": description.strip(),
            "sentiment": sentiment,
            "image_path": image_path,
            "created_at": datetime.utcnow(),
        }
    )

    return RedirectResponse(url="/gallery", status_code=303)
