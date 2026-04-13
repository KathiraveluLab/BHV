from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from bson import ObjectId
from bson.errors import InvalidId
from passlib.context import CryptContext
from pymongo.errors import DuplicateKeyError
from starlette.requests import Request

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY
from app.database import users_collection


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def get_user_by_email(email: str) -> Optional[dict[str, Any]]:
    return users_collection.find_one({"email": email})


def create_user(email: str, password: str, role: str = "user") -> bool:
    try:
        users_collection.insert_one(
            {
                "email": email,
                "password": hash_password(password),
                "role": role,
                "created_at": datetime.now(timezone.utc),
            }
        )
        return True
    except DuplicateKeyError:
        return False


def authenticate_user(email: str, password: str) -> Optional[dict[str, Any]]:
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user


def get_current_user_from_request(request: Request) -> Optional[dict[str, Any]]:
    token = request.cookies.get("access_token")

    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "", 1)

    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except InvalidId:
        return None

    if not user:
        return None

    user["id"] = str(user["_id"])
    return user
