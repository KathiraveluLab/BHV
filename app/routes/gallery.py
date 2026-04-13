from bson import ObjectId
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.database import images_collection
from app.services.auth_service import get_current_user_from_request
from app.services.image_service import delete_image_file, is_valid_sentiment


router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
SENTIMENT_CHOICES = ["positive", "neutral", "negative"]


@router.get("/")
def gallery_page(request: Request, user: Optional[dict] = Depends(get_current_user_from_request)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    images = list(images_collection.find({"user_id": user["id"]}).sort("created_at", -1))
    for image in images:
        image["id"] = str(image["_id"])
        image["sentiment"] = image.get("sentiment", "neutral")

    return templates.TemplateResponse(
        "gallery.html",
        {
            "request": request,
            "user": user,
            "images": images,
            "admin_view": False,
            "title": "My Gallery",
            "sentiments": SENTIMENT_CHOICES,
        },
    )


@router.post("/edit/{image_id}")
def edit_image(
    request: Request,
    image_id: str,
    title: str = Form(...),
    description: str = Form(""),
    sentiment: str = Form("neutral"),
    user: Optional[dict] = Depends(get_current_user_from_request),
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    try:
        image_doc = images_collection.find_one({"_id": ObjectId(image_id)})
    except InvalidId:
        return RedirectResponse(url="/gallery", status_code=303)

    if not image_doc or image_doc.get("user_id") != user["id"]:
        return RedirectResponse(url="/gallery", status_code=303)

    sentiment = sentiment.strip().lower()
    if not is_valid_sentiment(sentiment):
        return RedirectResponse(url="/gallery", status_code=303)

    update_data = {
        "title": title.strip(),
        "description": description.strip(),
        "sentiment": sentiment,
    }

    images_collection.update_one({"_id": ObjectId(image_id)}, {"$set": update_data})
    return RedirectResponse(url="/gallery", status_code=303)


@router.post("/delete/{image_id}")
def delete_image(request: Request, image_id: str, user: Optional[dict] = Depends(get_current_user_from_request)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    try:
        image = images_collection.find_one({"_id": ObjectId(image_id)})
    except InvalidId:
        return RedirectResponse(url="/gallery", status_code=303)

    if image and image.get("user_id") == user["id"]:
        delete_image_file(image.get("image_path", ""))
        images_collection.delete_one({"_id": ObjectId(image_id)})

    return RedirectResponse(url="/gallery", status_code=303)
