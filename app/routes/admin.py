from bson import ObjectId
from bson.errors import InvalidId
from typing import Optional

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.database import images_collection, users_collection
from app.services.auth_service import get_current_user_from_request
from app.services.image_service import delete_image_file


router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


def require_admin_user(user: Optional[dict] = Depends(get_current_user_from_request)):
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/auth/login"})
    if user.get("role") != "admin":
        raise HTTPException(status_code=303, headers={"Location": "/dashboard"})
    return user


@router.get("/")
def admin_panel(request: Request, user=Depends(require_admin_user)):

    images = list(images_collection.find().sort("created_at", -1))

    user_ids = {
        ObjectId(image["user_id"])
        for image in images
        if image.get("user_id")
    }

    owners = {
        str(user["_id"]): user
        for user in users_collection.find({"_id": {"$in": list(user_ids)}})
    }

    for image in images:
        image["id"] = str(image["_id"])
        image["sentiment"] = image.get("sentiment", "neutral")
        owner = owners.get(image.get("user_id"))
        image["owner_email"] = owner.get("email") if owner else "Unknown"

    return templates.TemplateResponse(
        "gallery.html",
        {
            "request": request,
            "user": user,
            "images": images,
            "admin_view": True,
            "title": "Admin Panel",
        },
    )


@router.post("/delete/{image_id}")
def delete_any_image(request: Request, image_id: str, user=Depends(require_admin_user)):

    try:
        image = images_collection.find_one({"_id": ObjectId(image_id)})
    except InvalidId:
        return RedirectResponse(url="/admin", status_code=303)

    if image:
        delete_image_file(image.get("image_path", ""))
        images_collection.delete_one({"_id": ObjectId(image_id)})

    return RedirectResponse(url="/admin", status_code=303)
